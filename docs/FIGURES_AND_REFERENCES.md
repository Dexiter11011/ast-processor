# Рисунки, подписи, последовательности и перекрёстные ссылки

Итерация 20 добавляет семантические подписи к рисункам/таблицам с нумерацией на основе полей Word и перекрёстными ссылками.

## Архитектура

```text
Image
  ↓
Figure (semantic)
  ↓
Caption paragraph
  ↓
SEQ Figure field
  ↓
Bookmark (figure-{slug})
  ↓
REF field (with \r \h switches)
```

```text
Table
  ↓
TableWithCaption (semantic)
  ↓
Caption paragraph (above table)
  ↓
SEQ Table field
  ↓
Bookmark (table-{slug})
  ↓
REF field
```

## Разделение ответственности

| Механизм | Роль |
|----------|------|
| Текст подписи | Человекочитаемое описание после номера последовательности |
| Поле SEQ | Word вычисляет 1, 2, 3… для каждого имени последовательности |
| Закладка | Стабильный якорь для REF (`figure-architecture`, а не `figure-1`) |
| Поле REF | Вставляет номер последовательности из закладки в месте ссылки |
| Стиль подписи | Оформление через тему (курсив, меньший размер) |

**Текст подписи ≠ номер SEQ ≠ закладка ≠ REF ≠ статический номер**

Приложение никогда не инкрементирует счётчики `figure_number`. Word вычисляет `SEQ Figure` / `SEQ Table` при открытии.

## Семантическая модель

Пакет: `md2docx.captions`

| Тип | Назначение |
|-----|------------|
| `CaptionKind` | `FIGURE`, `TABLE` |
| `SequenceKind` | Соответствует именам SEQ Word `"Figure"`, `"Table"` |
| `Caption` | `kind` + `text` (без поля `number`) |
| `Figure` | `image` + необязательная `caption` |
| `TableWithCaption` | `table` + необязательная `caption` |
| `CrossReference` | `target`, `kind`, `prefix` |
| `SequenceManager` | Только идентичность/метки — **не** счётчик |
| `CaptionService` | Рендерит рисунки, таблицы, перекрёстные ссылки |

## Структура подписи в OOXML

```text
w:p [Caption style]
├── w:bookmarkStart
├── "Figure "
├── SEQ Figure (complex field)
├── ". "
├── caption text runs
└── w:bookmarkEnd
```

Абзац перекрёстной ссылки:

```text
w:p [Normal]
├── "See "
├── "Figure "
└── REF figure-bookmark \r \h
```

- `\r` — вставить относительный номер последовательности из закладки
- `\h` — гиперссылка на закладку

Поля REF для заголовков (Итерация 19) сохраняют только `\h`.

## Расположение по умолчанию

| Объект | Порядок |
|--------|---------|
| Figure | Изображение → подпись (снизу) |
| Table | Подпись → таблица (сверху) |

## Именование закладок

Производится из текста подписи через `slugify()`:

| Текст подписи | Закладка |
|---------------|----------|
| Architecture overview | `figure-architecture-overview` |
| Configuration values | `table-configuration-values` |

Дубликаты получают числовой суффикс: `figure-architecture-1`.

## Внутренний API (синтаксис Markdown отложен)

Собирайте AST программно и конвертируйте:

```python
from pathlib import Path
from md2docx.pipeline import convert_ast_to_docx
from tests.figures_fixtures import build_interleaved_figures_tables_document

doc = build_interleaved_figures_tables_document()
convert_ast_to_docx(doc, Path("out.docx"), source_dir=Path("tests/fixtures"))
```

Зарегистрированные обработчики:

| Тип AST | Обработчик |
|---------|------------|
| `figure` | `FigureHandler` |
| `table_with_caption` | `TableWithCaptionHandler` |
| `cross_reference` | `CrossReferenceHandler` |

## Стили

Семантический стиль `caption` → OOXML `Caption` (курсив, 9pt, отступ после 120 twips).

Подписи к рисункам и таблицам используют один стиль Caption; вид задаётся семантически, а не отдельным стилем.

## Проверка

- Цели REF должны существовать в `BookmarkManager` на момент конвертации
- `ReferenceManager` проверяет типизированные перекрёстные ссылки (REF на рисунок должен указывать на закладку рисунка)
- `NavigationRegistry` отслеживает семантические цели в порядке документа
- Валидатор пакета сверяет инструкции REF с именами `w:bookmarkStart`
- Недопустимые имена закладок/последовательностей отклоняются белым списком парсера полей

## Связанные документы

- [`NAVIGATION.md`](NAVIGATION.md) — NavigationRegistry, LOF/LOT, переназначение закладок шаблона
- [`DYNAMIC_FIELDS.md`](DYNAMIC_FIELDS.md) — детали полей SEQ, REF
- [`REFERENCES_AND_TOC.md`](REFERENCES_AND_TOC.md) — закладки заголовков и гиперссылки
- [`THEMES.md`](THEMES.md) — стиль Caption в системе тем

## Остаётся (после Итерации 21)

- DSL подписей в Markdown (блочная директива или абзац с emphasis)
- Атрибут `title` изображения как источник подписи
- Полная локализация меток Figure/Table
