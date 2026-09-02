# Динамические поля DOCX

Итерация 19 добавляет семантические динамические поля Word, отдельные от плейсхолдеров шаблона и метаданных документа.

## Три механизма

| Механизм | Пример | Поведение |
|-----------|---------|----------|
| Static placeholder | `{{title}}` | Заменяется статическим текстом при слиянии шаблона |
| Document property | `dc:title` in `docProps/core.xml` | Метаданные пакета |
| Dynamic field | `PAGE`, `TITLE`, `REF` | Word пересчитывает при открытии документа |

`DocumentContext.title` может питать `{{title}}`, `dc:title` и поле `TITLE`, но это не один и тот же механизм. Все три читают из одного и того же разрешённого значения метаданных — см. [`DOCUMENT_METADATA.md`](DOCUMENT_METADATA.md).

`DocumentContext.date` — статические метаданные только для плейсхолдеров шаблона. Поле Word `DATE` динамическое и независимое.

## Поддерживаемые поля

| Поле | Статус | Форма OOXML |
|-------|--------|------------|
| `PAGE` | supported | `w:fldSimple` |
| `NUMPAGES` | supported | `w:fldSimple` |
| `DATE` | supported | `w:fldSimple` |
| `AUTHOR` | supported | `w:fldSimple` |
| `TITLE` | supported | `w:fldSimple` |
| `REF` | supported | complex field (`\h` headings; `\r \h` figure/table captions) |
| `SEQ` | supported in captions | complex field via `CaptionService` (internal API; Markdown DSL deferred) |
| `TOC` | supported | complex field (heading levels `\o "min-max"`) |
| List of Figures | supported | complex field (`TOC \h \z \c "Figure"`) — programmatic AST only |
| List of Tables | supported | complex field (`TOC \h \z \c "Table"`) — programmatic AST only |

## Директивы Markdown

```markdown
<!-- footer: page-numbers -->
<!-- header: title-field -->
<!-- header: author-field -->
<!-- header: date-field -->
<!-- field: date -->
<!-- field: ref architecture -->
<!-- field: seq Figure -->
<!-- toc -->
```

Они используют существующий конвейер колонтитулов и генерируют настоящие поля Word.

## Архитектура

```text
DynamicField
    ↓
FieldManager
    ↓
FieldRenderer
    ↓
md2docx.ooxml.api
    ↓
document.xml / header/footer parts
```

Обработчики не должны генерировать сырые `w:fldSimple`, `w:fldChar` или `w:instrText`.

## Настройки

Когда документ содержит динамические поля, writer генерирует `word/settings.xml` с:

```xml
<w:updateFields w:val="true"/>
```

CLI:

```bash
md2docx input.md --update-fields
md2docx input.md --no-update-fields
```

По умолчанию: обновлять поля при открытии, когда документ содержит динамические поля.

## Вычисление во время выполнения

Динамические поля генерируются для WordprocessingML. Их отображаемый результат пересчитывается Microsoft Word или LibreOffice при открытии документа или обновлении полей. CLI не вычисляет результаты полей.

См. также [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md) для статических плейсхолдеров шаблона и [`FIGURES_AND_REFERENCES.md`](FIGURES_AND_REFERENCES.md) для подписей рисунков/таблиц с SEQ и REF. См. [`NAVIGATION.md`](NAVIGATION.md) для списков рисунков/таблиц и реестра навигации.
