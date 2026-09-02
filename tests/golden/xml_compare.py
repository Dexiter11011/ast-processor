"""Structural XML comparison for golden tests."""

from __future__ import annotations

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"

W_T_TAG = f"{{{W_NS}}}t"

_NS_PREFIX = {
    W_NS: "w",
    R_NS: "r",
    XML_NS: "xml",
}


def pretty_xml(data: bytes) -> str:
    root = etree.fromstring(data)
    return etree.tostring(root, pretty_print=True, encoding="unicode")


def _normalize_text(value: str | None, *, tag: str) -> str | None:
    if value is None or value == "":
        return None
    if tag == W_T_TAG:
        return value
    if value.strip() == "":
        return None
    return value


def _normalize_tail(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    if value.strip() == "":
        return None
    return value


def _tag_label(tag: str) -> str:
    if not tag.startswith("{"):
        return tag
    uri, local = tag[1:].split("}", 1)
    prefix = _NS_PREFIX.get(uri)
    return f"{prefix}:{local}" if prefix else local


def compare_elements(
    expected: etree._Element,
    actual: etree._Element,
    *,
    path: str = "",
) -> list[str]:
    """Return human-readable diff lines; empty list means trees match."""
    label = path or _tag_label(expected.tag)
    diffs: list[str] = []

    if expected.tag != actual.tag:
        diffs.append(f"{label}: tag {expected.tag!r} != {actual.tag!r}")
        return diffs

    if dict(expected.attrib) != dict(actual.attrib):
        diffs.append(
            f"{label}: attributes differ\n"
            f"  expected: {dict(expected.attrib)!r}\n"
            f"  actual:   {dict(actual.attrib)!r}"
        )

    exp_text = _normalize_text(expected.text, tag=expected.tag)
    act_text = _normalize_text(actual.text, tag=actual.tag)
    if exp_text != act_text:
        diffs.append(f"{label}: text {exp_text!r} != {act_text!r}")

    exp_children = list(expected)
    act_children = list(actual)
    if len(exp_children) != len(act_children):
        diffs.append(
            f"{label}: child count {len(exp_children)} != {len(act_children)}"
        )
    else:
        for index, (exp_child, act_child) in enumerate(zip(exp_children, act_children)):
            child_path = f"{label}/{_tag_label(exp_child.tag)}[{index}]"
            diffs.extend(compare_elements(exp_child, act_child, path=child_path))

    exp_tail = _normalize_tail(expected.tail)
    act_tail = _normalize_tail(actual.tail)
    if exp_tail != act_tail:
        diffs.append(f"{label}: tail {exp_tail!r} != {act_tail!r}")

    return diffs


def assert_document_xml_equal(expected: bytes, actual: bytes) -> None:
    """Assert two word/document.xml payloads are structurally identical."""
    expected_root = etree.fromstring(expected)
    actual_root = etree.fromstring(actual)
    diffs = compare_elements(expected_root, actual_root)
    if not diffs:
        return
    message = "document.xml differs structurally:\n" + "\n".join(f"  - {line}" for line in diffs)
    message += "\n\n--- expected ---\n" + pretty_xml(expected)
    message += "\n--- actual ---\n" + pretty_xml(actual)
    message += "\n\nRe-generate golden files: python scripts/update-golden.py"
    raise AssertionError(message)
