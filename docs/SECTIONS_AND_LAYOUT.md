# Секции, макет страницы, колонтитулы

Итерация 11 добавляет структуру секций документа отдельно от Style System и NumberingManager.

## Четыре слоя

```text
Style System     → paragraph/run/table appearance (Heading1, Normal, TableGrid)
NumberingManager → list numId/ilvl
SectionManager   → page layout, section breaks, headers/footers
Table OOXML      → grid, borders, cell layout
```

## Модель секции

```text
Section
├── PageLayout (PageSize, Orientation, optional PageMargins)
├── header_rel_id (optional)
└── footer_rel_id (optional)
```

Документ по умолчанию: **одна секция A4 portrait** с финальным `w:sectPr` на `w:body`.

В многосекционных документах inline `w:sectPr` размещается на **последнем абзаце** каждой предыдущей секции; финальная секция использует `w:sectPr` на уровне body.

## Разрыв страницы и разрыв секции

| Функция | OOXML | Директива Markdown |
|---------|-------|-------------------|
| Page break | `<w:br w:type="page"/>` | `<!-- pagebreak -->` |
| Section break | inline `w:sectPr` + new section | `<!-- section: landscape -->` |

Разрыв страницы **не** меняет свойства секции. Разрыв секции начинает новую `Section` с собственным макетом и необязательными header/footer.

## Директивы header / footer

```markdown
<!-- header: Document Title -->
<!-- footer: Page 1 -->
```

Они задают содержимое header/footer для **текущей секции**. Части header/footer переиспользуют те же сборщики OOXML абзацев/runs и стиль `Normal` — отдельного HeaderParagraphStyle нет.

Структура пакета:

```text
word/document.xml
    ├── headerReference → word/header1.xml
    └── footerReference → word/footer1.xml
```

## Спецификации макета

Примеры директив секции:

| Директива | Результат |
|-----------|-----------|
| `<!-- section: a4 -->` | A4 portrait |
| `<!-- section: letter -->` | Letter portrait |
| `<!-- section: landscape -->` | A4 landscape |
| `<!-- section: a4 margins=720,720,720,720 -->` | A4 с пользовательскими полями (twips) |

Единицы: **twips** (1/1440 дюйма), согласованно с OOXML `pgSz` / `pgMar`.

## Компоненты

| Компонент | Расположение |
|-----------|--------------|
| `PageLayout`, `Section` | `sections/definition.py` |
| `SectionManager` | `sections/manager.py` |
| `build_sect_pr()` | `ooxml/section.py` |
| Части header/footer | `ooxml/header_footer.py` |
| Page break | `ooxml/page_break.py` |
| Блочные директивы | `parser/block_directive.py` |

## Тесты

- `tests/sections/` — модель макета
- `tests/ooxml/test_section.py` — сериализация sectPr
- `tests/integration/test_sections_layout.py` — page break, landscape, header/footer
- `tests/fixtures/sections-integration.md` — комбинированная интеграционная фикстура

См. также [`STYLE_SYSTEM.md`](STYLE_SYSTEM.md), [`LISTS_AND_TABLES.md`](LISTS_AND_TABLES.md), [`RENDERING_CONTEXT.md`](RENDERING_CONTEXT.md).
