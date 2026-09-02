"""Safe inline HTML to semantic AST conversion."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from md2docx.ast.types import Emphasis, InlineNode, LineBreak, Link, Strikethrough, Strong, Text
from md2docx.parser.errors import HtmlParseError

_TAG_RE = re.compile(r"^<\s*(/?)\s*([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)(/?)\s*>$")
_ATTR_RE = re.compile(r'([a-zA-Z_:][a-zA-Z0-9_:\-]*)\s*=\s*"([^"]*)"')

ALLOWED_TAGS = frozenset({"strong", "b", "em", "i", "del", "s", "br", "span", "a"})
BLOCKED_TAGS = frozenset(
    {
        "script",
        "style",
        "iframe",
        "object",
        "embed",
        "form",
        "input",
        "img",
        "div",
        "section",
        "table",
        "video",
        "audio",
        "meta",
        "link",
        "base",
    }
)
ALLOWED_SCHEMES = frozenset({"http", "https", "mailto"})


@dataclass(frozen=True)
class HtmlTag:
    name: str
    closing: bool
    self_closing: bool
    attrs: dict[str, str]


def parse_html_tag(content: str) -> HtmlTag | None:
    match = _TAG_RE.match(content.strip())
    if match is None:
        return None
    closing, name, attr_text, self_close = match.groups()
    name = name.lower()
    attrs = {key.lower(): html.unescape(value) for key, value in _ATTR_RE.findall(attr_text)}
    return HtmlTag(name=name, closing=bool(closing), self_closing=bool(self_close), attrs=attrs)


def validate_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        raise HtmlParseError(f'unsafe URL scheme: {scheme or "(missing)"}')
    return url.strip()


def wrap_html_tag(tag_name: str, children: list[InlineNode]) -> InlineNode:
    if tag_name in {"strong", "b"}:
        return Strong(children=children)
    if tag_name in {"em", "i"}:
        return Emphasis(children=children)
    if tag_name in {"del", "s"}:
        return Strikethrough(children=children)
    if tag_name == "span":
        return _unwrap_span(children)
    raise HtmlParseError(f"unsupported HTML element: {tag_name}")


def _unwrap_span(children: list[InlineNode]) -> InlineNode:
    if len(children) == 1:
        return children[0]
    if not children:
        return Text(value="")
    return Strong(children=children)


def build_link_from_html(attrs: dict[str, str], children: list[InlineNode]) -> Link:
    href = attrs.get("href")
    if not href:
        raise HtmlParseError("HTML anchor requires href attribute")
    return Link(url=validate_url(href), title=attrs.get("title"), children=children)


_BLOCK_TAG_RE = re.compile(r"^<\s*([a-zA-Z][a-zA-Z0-9]*)\b")


def block_tag_name(content: str) -> str | None:
    match = _BLOCK_TAG_RE.match(content.strip())
    return match.group(1).lower() if match else None


def validate_html_tag(
    content: str,
    *,
    path: str | None = None,
    line: int | None = None,
) -> HtmlTag:
    """Parse and validate an inline HTML token; raise HtmlParseError when unsafe."""
    tag = parse_html_tag(content)
    if tag is None:
        raise HtmlParseError(f"malformed HTML: {content.strip()}", path=path, line=line)
    if tag.name in BLOCKED_TAGS:
        raise HtmlParseError(f"unsupported HTML element: {tag.name}", path=path, line=line)
    if not tag.closing and tag.name not in ALLOWED_TAGS:
        raise HtmlParseError(f"unsupported HTML element: {tag.name}", path=path, line=line)
    return tag


def wrap_html_close_tag(
    tag_name: str,
    attrs: dict[str, str],
    children: list[InlineNode],
) -> InlineNode:
    if tag_name == "a":
        return build_link_from_html(attrs, children)
    if tag_name == "br":
        return LineBreak()
    return wrap_html_tag(tag_name, children)
