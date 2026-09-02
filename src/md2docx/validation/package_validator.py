"""Validate OOXML DOCX package structure, XML, relationships, and references."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from urllib.parse import unquote

from lxml import etree

from md2docx.ooxml.content_types import _EXT_TO_CT
from md2docx.ooxml.xml_builder import R_NS, W_NS, w_attr
from md2docx.validation.errors import ValidationReport
from md2docx.validation.field_validator import collect_bookmark_names, validate_fields_in_part

PKG_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

REQUIRED_PARTS = (
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
    "word/_rels/document.xml.rels",
    "word/styles.xml",
)

OVERRIDE_CONTENT_TYPES = {
    "/word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
    "/word/styles.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
    "/word/numbering.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml",
    "/docProps/core.xml": "application/vnd.openxmlformats-package.core-properties+xml",
    "/docProps/app.xml": "application/vnd.openxmlformats-officedocument.extended-properties+xml",
    "/word/settings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
}

DEFAULT_CONTENT_TYPES = {
    "rels": "application/vnd.openxmlformats-package.relationships+xml",
    "xml": "application/xml",
}

R_ID_ATTR = f"{{{R_NS}}}id"
R_EMBED_ATTR = f"{{{R_NS}}}embed"

_IMAGE_MAGIC = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
    "gif": (b"GIF87a", b"GIF89a"),
}


@dataclass
class DocxPackage:
    parts: dict[str, bytes] = field(default_factory=dict)

    @classmethod
    def from_path(cls, path: Path) -> DocxPackage:
        try:
            with zipfile.ZipFile(path, "r") as zf:
                return cls.from_zipfile(zf)
        except zipfile.BadZipFile:
            return cls(parts={})

    @classmethod
    def from_zipfile(cls, zf: zipfile.ZipFile) -> DocxPackage:
        parts = {name: zf.read(name) for name in zf.namelist()}
        return cls(parts=parts)

    @classmethod
    def from_bytes(cls, data: bytes) -> DocxPackage:
        import io

        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            return cls.from_zipfile(zf)


def validate_docx(path: Path | str) -> ValidationReport:
    """Run full validation on a DOCX file and return a report."""
    return DocxValidator(DocxPackage.from_path(Path(path))).validate()


def validate_docx_bytes(data: bytes) -> ValidationReport:
    """Run full validation on in-memory DOCX bytes."""
    return DocxValidator(DocxPackage.from_bytes(data)).validate()


class DocxValidator:
    """Validate package integrity, XML, content types, relationships, and references."""

    def __init__(self, package: DocxPackage) -> None:
        self.package = package
        self.report = ValidationReport()
        self._parsed_xml: dict[str, etree._Element] = {}
        self._content_type_map: dict[str, str] = {}

    def validate(self) -> ValidationReport:
        self._validate_zip_integrity()
        self._validate_required_parts()
        self._validate_all_xml_well_formed()
        self._validate_unicode_declarations()
        self._validate_content_types()
        self._validate_root_relationships()
        self._validate_document_relationships()
        self._validate_relationship_targets_exist()
        self._validate_document_structure()
        self._validate_styles()
        self._validate_numbering()
        self._validate_relationship_references()
        self._validate_bookmarks_and_anchors()
        self._validate_dynamic_fields()
        self._validate_media()
        return self.report

    def _validate_zip_integrity(self) -> None:
        import io

        try:
            with zipfile.ZipFile(io.BytesIO(self._zip_bytes()), "r") as zf:
                bad = zf.testzip()
                if bad is not None:
                    self.report.add("package", f"corrupt ZIP entry: {bad}")
        except zipfile.BadZipFile as exc:
            self.report.add("package", f"invalid ZIP archive: {exc}")

    def _zip_bytes(self) -> bytes:
        import io

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name in sorted(self.package.parts):
                zf.writestr(name, self.package.parts[name])
        return buf.getvalue()

    def _validate_required_parts(self) -> None:
        for part in REQUIRED_PARTS:
            if part not in self.package.parts:
                self.report.add("package", f"missing required part: {part}", part=part)

    def _validate_all_xml_well_formed(self) -> None:
        for part, data in self.package.parts.items():
            if not (part.endswith(".xml") or part.endswith(".rels")):
                continue
            try:
                self._parsed_xml[part] = etree.fromstring(data)
            except etree.XMLSyntaxError as exc:
                self.report.add("xml", f"malformed XML: {exc}", part=part)

    def _validate_unicode_declarations(self) -> None:
        for part, data in self.package.parts.items():
            if not (part.endswith(".xml") or part.endswith(".rels")):
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError as exc:
                self.report.add("unicode", f"not valid UTF-8: {exc}", part=part)
                continue
            if "encoding=\"UTF-8\"" not in text and "encoding='UTF-8'" not in text:
                self.report.add(
                    "unicode",
                    "XML declaration should specify UTF-8 encoding",
                    part=part,
                    severity="warning",
                )

    def _validate_content_types(self) -> None:
        root = self._parsed_xml.get("[Content_Types].xml")
        if root is None:
            return

        defaults: dict[str, str] = {}
        overrides: dict[str, str] = {}
        for child in root:
            local = _local_name(child.tag)
            if local == "Default":
                defaults[child.get("Extension", "")] = child.get("ContentType", "")
            elif local == "Override":
                overrides[child.get("PartName", "")] = child.get("ContentType", "")

        for ext, expected in {**DEFAULT_CONTENT_TYPES, **_EXT_TO_CT}.items():
            if ext in defaults and defaults[ext] != expected:
                self.report.add(
                    "content_types",
                    f"Default Extension={ext} has {defaults[ext]!r}, expected {expected!r}",
                    part="[Content_Types].xml",
                )

        for part_name, expected in OVERRIDE_CONTENT_TYPES.items():
            if part_name.lstrip("/") in self.package.parts:
                actual = overrides.get(part_name)
                if actual != expected:
                    self.report.add(
                        "content_types",
                        f"Override PartName={part_name} has {actual!r}, expected {expected!r}",
                        part="[Content_Types].xml",
                    )

        header_ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"
        footer_ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
        for part_name, actual in overrides.items():
            if part_name.startswith("/word/header") and actual != header_ct:
                self.report.add(
                    "content_types",
                    f"Override PartName={part_name} has {actual!r}, expected {header_ct!r}",
                    part="[Content_Types].xml",
                )
            if part_name.startswith("/word/footer") and actual != footer_ct:
                self.report.add(
                    "content_types",
                    f"Override PartName={part_name} has {actual!r}, expected {footer_ct!r}",
                    part="[Content_Types].xml",
                )

        for part in self.package.parts:
            if part == "[Content_Types].xml":
                continue
            resolved = self._resolve_content_type(part, defaults, overrides)
            if resolved is None:
                self.report.add(
                    "content_types",
                    f"no Default or Override entry covers part {part!r}",
                    part="[Content_Types].xml",
                )
            self._content_type_map[part] = resolved or ""

    def _resolve_content_type(
        self,
        part: str,
        defaults: dict[str, str],
        overrides: dict[str, str],
    ) -> str | None:
        override_key = f"/{part}"
        if override_key in overrides:
            return overrides[override_key]
        ext = _part_extension(part)
        if ext in defaults:
            return defaults[ext]
        return None

    def _validate_root_relationships(self) -> None:
        self._validate_relationships_file(
            "_rels/.rels",
            base="",
            required_types={
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument": "word/document.xml",
            },
        )

    def _validate_document_relationships(self) -> None:
        self._validate_relationships_file(
            "word/_rels/document.xml.rels",
            base="word/",
            required_types={
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles": "styles.xml",
            },
        )

    def _validate_relationships_file(
        self,
        rels_part: str,
        *,
        base: str,
        required_types: dict[str, str],
    ) -> dict[str, dict[str, str]]:
        rels: dict[str, dict[str, str]] = {}
        root = self._parsed_xml.get(rels_part)
        if root is None:
            return rels

        seen_ids: set[str] = set()
        seen_types: dict[str, str] = {}
        for rel in root:
            if _local_name(rel.tag) != "Relationship":
                continue
            rel_id = rel.get("Id", "")
            rel_type = rel.get("Type", "")
            target = rel.get("Target", "")
            target_mode = rel.get("TargetMode", "")
            if not rel_id:
                self.report.add("relationships", "Relationship missing Id", part=rels_part)
                continue
            if rel_id in seen_ids:
                self.report.add("relationships", f"duplicate relationship Id {rel_id!r}", part=rels_part)
            seen_ids.add(rel_id)
            if rel_type in seen_types and seen_types[rel_type] != target:
                self.report.add(
                    "relationships",
                    f"duplicate relationship Type {rel_type!r}",
                    part=rels_part,
                    severity="warning",
                )
            seen_types[rel_type] = target
            rels[rel_id] = {
                "Type": rel_type,
                "Target": target,
                "TargetMode": target_mode,
                "resolved": self._resolve_relationship_target(base, target, target_mode),
            }

        for rel_type, target in required_types.items():
            if target not in {info["Target"] for info in rels.values()}:
                self.report.add(
                    "relationships",
                    f"missing required relationship target {target!r} ({rel_type})",
                    part=rels_part,
                )
        return rels

    def _validate_relationship_targets_exist(self) -> None:
        doc_rels = self._relationship_index("word/_rels/document.xml.rels", base="word/")
        root_rels = self._relationship_index("_rels/.rels", base="")

        for rel_id, info in doc_rels.items():
            if info["TargetMode"] == "External":
                continue
            target = info["resolved"]
            if target not in self.package.parts:
                self.report.add(
                    "relationships",
                    f"{rel_id} Target resolves to missing part {target!r}",
                    part="word/_rels/document.xml.rels",
                )

        for rel_id, info in root_rels.items():
            if info["TargetMode"] == "External":
                continue
            target = info["resolved"]
            if target not in self.package.parts:
                self.report.add(
                    "relationships",
                    f"{rel_id} Target resolves to missing part {target!r}",
                    part="_rels/.rels",
                )

    def _relationship_index(self, rels_part: str, *, base: str) -> dict[str, dict[str, str]]:
        index: dict[str, dict[str, str]] = {}
        root = self._parsed_xml.get(rels_part)
        if root is None:
            return index
        for rel in root:
            if _local_name(rel.tag) != "Relationship":
                continue
            rel_id = rel.get("Id", "")
            target = rel.get("Target", "")
            target_mode = rel.get("TargetMode", "")
            index[rel_id] = {
                "Type": rel.get("Type", ""),
                "Target": target,
                "TargetMode": target_mode,
                "resolved": self._resolve_relationship_target(base, target, target_mode),
            }
        return index

    def _validate_document_structure(self) -> None:
        root = self._parsed_xml.get("word/document.xml")
        if root is None:
            return
        body = root.find(f"{{{W_NS}}}body")
        if body is None:
            self.report.add("document", "missing w:body", part="word/document.xml")
            return
        children = list(body)
        if not children:
            self.report.add("document", "w:body is empty", part="word/document.xml")
            return
        if _local_name(children[-1].tag) != "sectPr":
            self.report.add("document", "w:body must end with w:sectPr", part="word/document.xml")
        pg_sz = body.find(f".//{{{W_NS}}}sectPr/{{{W_NS}}}pgSz")
        if pg_sz is None:
            self.report.add("document", "missing w:sectPr/w:pgSz", part="word/document.xml")

    def _validate_styles(self) -> None:
        styles_root = self._parsed_xml.get("word/styles.xml")
        doc_root = self._parsed_xml.get("word/document.xml")
        if styles_root is None or doc_root is None:
            return

        defined = {
            style.get(w_attr("styleId"))
            for style in styles_root.findall(f"{{{W_NS}}}style")
            if style.get(w_attr("styleId"))
        }
        if "Normal" not in defined:
            self.report.add("styles", "styles.xml must define Normal style", part="word/styles.xml")

        for el in doc_root.iter():
            if _local_name(el.tag) == "pStyle":
                style_id = el.get(w_attr("val"), "")
                if style_id and style_id not in defined:
                    self.report.add(
                        "styles",
                        f"document references unknown paragraph style {style_id!r}",
                        part="word/document.xml",
                    )
            elif _local_name(el.tag) == "rStyle":
                style_id = el.get(w_attr("val"), "")
                if style_id and style_id not in defined:
                    self.report.add(
                        "styles",
                        f"document references unknown run style {style_id!r}",
                        part="word/document.xml",
                    )

    def _validate_numbering(self) -> None:
        doc_root = self._parsed_xml.get("word/document.xml")
        numbering_root = self._parsed_xml.get("word/numbering.xml")
        if doc_root is None:
            return

        referenced = {
            el.get(w_attr("val"))
            for el in doc_root.iter(f"{{{W_NS}}}numId")
            if el.get(w_attr("val"))
        }
        if referenced and numbering_root is None:
            self.report.add(
                "numbering",
                f"document references numId {sorted(referenced)!r} but word/numbering.xml is missing",
                part="word/document.xml",
            )
            return
        if numbering_root is None:
            return

        defined = {
            num.get(w_attr("numId"))
            for num in numbering_root.findall(f"{{{W_NS}}}num")
            if num.get(w_attr("numId"))
        }
        for num_id in referenced:
            if num_id not in defined:
                self.report.add(
                    "numbering",
                    f"document references unknown numId {num_id!r}",
                    part="word/document.xml",
                )

    def _validate_relationship_references(self) -> None:
        doc_root = self._parsed_xml.get("word/document.xml")
        doc_rels = self._relationship_index("word/_rels/document.xml.rels", base="word/")
        if doc_root is None:
            return

        referenced: set[str] = set()
        for el in doc_root.iter():
            for attr in (R_ID_ATTR, R_EMBED_ATTR):
                rel_id = el.get(attr)
                if rel_id:
                    referenced.add(rel_id)

        for rel_id in sorted(referenced):
            if rel_id not in doc_rels:
                self.report.add(
                    "references",
                    f"dangling relationship reference {rel_id!r} in word/document.xml",
                    part="word/document.xml",
                )

        defined = set(doc_rels)
        for rel_id in sorted(defined):
            if rel_id not in referenced and doc_rels[rel_id]["TargetMode"] != "External":
                rel_type = doc_rels[rel_id]["Type"]
                if "image" in rel_type or "numbering" in rel_type or "styles" in rel_type:
                    if rel_id not in referenced:
                        # styles/numbering are package-level refs from document settings sometimes;
                        # our generator only uses r:id on hyperlinks and r:embed on images in body.
                        if "styles" in rel_type or "numbering" in rel_type or "header" in rel_type or "footer" in rel_type:
                            continue
                self.report.add(
                    "references",
                    f"unused relationship {rel_id!r} ({doc_rels[rel_id]['Target']})",
                    part="word/_rels/document.xml.rels",
                    severity="warning",
                )

    def _validate_bookmarks_and_anchors(self) -> None:
        doc_root = self._parsed_xml.get("word/document.xml")
        if doc_root is None:
            return

        bookmark_starts = doc_root.findall(f".//{{{W_NS}}}bookmarkStart")
        bookmark_ids: dict[str, list[str]] = {}
        bookmark_names: set[str] = set()
        for start in bookmark_starts:
            bookmark_id = start.get(w_attr("id"))
            name = start.get(w_attr("name"))
            if bookmark_id is not None:
                bookmark_ids.setdefault(bookmark_id, []).append(name or "")
            if name:
                bookmark_names.add(name)

        for bookmark_id, names in bookmark_ids.items():
            if len(names) > 1:
                self.report.add(
                    "bookmarks",
                    f"duplicate bookmark id {bookmark_id!r}",
                    part="word/document.xml",
                )

        for hyper in doc_root.findall(f".//{{{W_NS}}}hyperlink"):
            anchor = hyper.get(w_attr("anchor"))
            if not anchor:
                continue
            if anchor not in bookmark_names:
                self.report.add(
                    "references",
                    f"hyperlink anchor {anchor!r} has no matching bookmark",
                    part="word/document.xml",
                )

    def _validate_dynamic_fields(self) -> None:
        doc_root = self._parsed_xml.get("word/document.xml")
        if doc_root is None:
            return
        bookmark_names = collect_bookmark_names(doc_root)
        validate_fields_in_part(
            doc_root,
            part_name="word/document.xml",
            bookmark_names=bookmark_names,
            report=self.report,
        )
        for part_name, root in self._parsed_xml.items():
            if part_name.startswith("word/header") or part_name.startswith("word/footer"):
                validate_fields_in_part(
                    root,
                    part_name=part_name,
                    bookmark_names=bookmark_names,
                    report=self.report,
                )

    def _validate_media(self) -> None:
        doc_rels = self._relationship_index("word/_rels/document.xml.rels", base="word/")
        image_rels = {
            rel_id: info
            for rel_id, info in doc_rels.items()
            if info["Type"].endswith("/image")
        }

        media_parts = {part for part in self.package.parts if part.startswith("word/media/")}
        rel_media = {info["resolved"] for info in image_rels.values()}

        for part in sorted(media_parts):
            if part not in rel_media:
                self.report.add("media", f"media part {part!r} has no image relationship", part=part)
            self._validate_media_bytes(part)

        for rel_id, info in image_rels.items():
            target = info["resolved"]
            if target not in self.package.parts:
                self.report.add(
                    "media",
                    f"image relationship {rel_id} points to missing part {target!r}",
                    part="word/_rels/document.xml.rels",
                )

        doc_root = self._parsed_xml.get("word/document.xml")
        if doc_root is None:
            return
        for el in doc_root.iter():
            rel_id = el.get(R_EMBED_ATTR)
            if not rel_id:
                continue
            if rel_id not in image_rels:
                self.report.add(
                    "media",
                    f"r:embed={rel_id!r} is not an image relationship",
                    part="word/document.xml",
                )

    def _validate_media_bytes(self, part: str) -> None:
        data = self.package.parts.get(part, b"")
        ext = PurePosixPath(part).suffix.lstrip(".").lower()
        magic = _IMAGE_MAGIC.get(ext)
        if magic is None:
            return
        if isinstance(magic, tuple):
            if not any(data.startswith(prefix) for prefix in magic):
                self.report.add("media", f"file content does not match {ext} format", part=part)
        elif not data.startswith(magic):
            self.report.add("media", f"file content does not match {ext} format", part=part)

    @staticmethod
    def _resolve_relationship_target(base: str, target: str, target_mode: str) -> str:
        if target_mode == "External":
            return target
        joined = PurePosixPath(unquote(base)) / PurePosixPath(unquote(target))
        normalized = str(joined).replace("\\", "/")
        while "/../" in normalized or normalized.endswith("/.."):
            normalized = str(PurePosixPath(normalized))
        return normalized.lstrip("/")


def _local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _part_extension(part: str) -> str:
    name = PurePosixPath(part).name
    if name.endswith(".rels"):
        return "rels"
    return PurePosixPath(part).suffix.lstrip(".").lower()
