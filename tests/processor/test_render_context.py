"""RenderContext and InlineFormatting unit tests."""

from md2docx.processor.inline_formatting import InlineFormatting, RenderContext


def test_default_render_context_has_plain_formatting():
    ctx = RenderContext.default()
    assert ctx.formatting == InlineFormatting()
    assert ctx.formatting.bold is False
    assert ctx.formatting.italic is False
    assert ctx.formatting.code is False


def test_inline_formatting_with_bold():
    fmt = InlineFormatting().with_bold()
    assert fmt.bold is True
    assert fmt.italic is False


def test_inline_formatting_with_italic():
    fmt = InlineFormatting().with_italic()
    assert fmt.italic is True
    assert fmt.bold is False


def test_inline_formatting_with_code():
    fmt = InlineFormatting().with_code()
    assert fmt.code is True
    assert fmt.bold is False


def test_nested_derive_bold_then_italic():
    parent = RenderContext.default()
    bold_ctx = parent.derive(formatting=parent.formatting.with_bold())
    nested = bold_ctx.derive(formatting=bold_ctx.formatting.with_italic())
    assert nested.formatting.bold is True
    assert nested.formatting.italic is True


def test_derive_does_not_mutate_parent():
    parent = RenderContext.default()
    child = parent.derive(formatting=parent.formatting.with_bold())
    assert parent.formatting.bold is False
    assert child.formatting.bold is True
