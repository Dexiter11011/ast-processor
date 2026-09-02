"""Front matter parser tests."""

from md2docx.parser.front_matter import parse_document_metadata, split_front_matter


def test_split_front_matter():
    source = "---\ntitle: Hello\nauthor: Bob\ndate: 2026-08-31\n---\n\nBody text."
    raw, body = split_front_matter(source)
    assert raw == {"title": "Hello", "author": "Bob", "date": "2026-08-31"}
    assert body == "Body text."


def test_split_front_matter_ignores_config_keys():
    source = "---\ntitle: Hello\ntheme: corporate\n---\n\nBody."
    raw, body = split_front_matter(source)
    assert raw == {"title": "Hello"}
    assert "theme" not in raw


def test_split_front_matter_missing():
    raw, body = split_front_matter("No front matter here.")
    assert raw == {}
    assert body == "No front matter here."


def test_parse_document_metadata():
    metadata = parse_document_metadata(
        {
            "title": "T",
            "author": "A",
            "subject": "S",
            "keywords": "k1, k2",
        }
    )
    assert metadata.title == "T"
    assert metadata.author == "A"
    assert metadata.subject == "S"
    assert metadata.keywords == "k1, k2"
    assert metadata.has_values() is True
