# Система стилей

Итерация 9 вводит управляемую данными систему стилей, которая разделяет семантику Markdown и визуальное представление.

## Проблема

Ранее `word/styles.xml` собирался жёстко закодированными функциями в `ooxml/styles.py`, а обработчики использовали тонкий резолвер `StyleManager`. Два подхода не были унифицированы, и семантические роли часто совпадали с OOXML styleIds (`Heading1`, `Quote`, …).

## Архитектура

```text
Markdown AST
     ↓
Element Handler (semantic role)
     ↓
StyleManager.resolve_semantic("heading", level=1)  →  "heading1"
StyleManager.to_ooxml("heading1")                  →  "Heading1"
     ↓
document.xml: <w:pStyle w:val="Heading1"/>
     ↓
StyleRegistry + DefaultTheme
     ↓
StylesXmlWriter → word/styles.xml
```

## Компоненты

| Компонент | Расположение | Роль |
|-----------|----------|------|
| `StyleDefinition` | `styles/definition.py` | Неизменяемые свойства абзаца/run |
| `StyleRegistry` | `styles/registry.py` | Один семантический id → одно определение |
| `DefaultTheme` | `styles/theme.py` | Встроенный набор стилей |
| `StyleManager` | `processor/style_manager.py` | Фасад обработчиков над реестром |
| `StylesXmlWriter` | `ooxml/styles_xml_writer.py` | Сериализует реестр в XML |

## Семантические стили

| Semantic id | OOXML styleId | Используется |
|-------------|---------------|---------|
| `normal` | Normal | Paragraph |
| `heading1`–`heading3` | Heading1–Heading3 | Heading |
| `quote` | Quote | Blockquote |
| `code_block` | NoSpacing | Fenced code block |
| `inline_code` | Code | Inline code (character style) |
| `list_bullet` / `list_number` | ListBullet / ListNumber | Устаревшие стили в реестре (не генерируются обработчиками) |
| `list_paragraph` | ListParagraph | Все абзацы элементов списка |
| `table` | TableGrid | Tables via `w:tblStyle` |

## Система стилей ≠ контекст рендеринга

Это разные концепции:

**Style System** — какой это тип элемента документа?

```text
Heading1, Quote, Normal, NoSpacing
```

**Render Context** — какое inline-форматирование активно?

```text
bold, italic, code
```

Пример — `# **Hello**`:

```text
Paragraph style: Heading1   (Style System)
Run formatting:  bold=true  (RenderContext)
```

См. также [`RENDERING_CONTEXT.md`](RENDERING_CONTEXT.md).

## Нецели (эта итерация)

- YAML/JSON themes, CLI `--theme`, DOCX templates
- Новые возможности Markdown

Темы документа: см. [`THEMES.md`](THEMES.md).

Детали нумерации списков и макета таблиц: [`LISTS_AND_TABLES.md`](LISTS_AND_TABLES.md).

## Тесты

- `tests/styles/` — registry, theme, inheritance
- `tests/elements/test_handler_semantic_styles.py` — handler role mapping
- `tests/integration/test_style_system_integration.py` — style + inline formatting
- `tests/golden/test_styles_xml.py` — default styles.xml snapshot
