# Система тем документа

Итерация 15 вводит подключаемую **тему документа (Document Theme)**, которая управляет визуальным представлением независимо от парсинга Markdown и обработчиков элементов.

## Архитектура

```text
Markdown AST
     ↓
Semantic role (handlers)
     ↓
StyleManager
     ↑
DocumentTheme
     ↓
ThemeResolver → StyleRegistry
     ↓
StylesXmlWriter → word/styles.xml
```

Параллельный путь inline (без изменений):

```text
AST → RenderContext → InlineFormatting → run properties
```

## Владение

| Компонент | Владеет |
|-----------|------|
| `DocumentTheme` | визуальными токенами + конфигурацией семантических стилей |
| `ThemeResolver` | Токены темы → `StyleRegistry` |
| `StyleRegistry` | разрешёнными определениями семантических стилей |
| `StyleManager` | поиском стилей для обработчиков |
| `StylesXmlWriter` | `StyleDefinition` → `styles.xml` |
| Handlers | только выбором семантической роли |
| `RenderContext` | локальным inline-форматированием (`bold`, `italic`, `strike`, `code`) |
| `NumberingManager` | `numId` / `ilvl` (не визуальная тема) |
| `SectionManager` | явными переопределениями секций поверх значений страницы темы по умолчанию |

## Токены темы

Темы настраивают представление через неизменяемые группы токенов в [`styles/tokens.py`](../src/md2docx/styles/tokens.py):

- `TypographyTokens` — шрифты и размеры основного текста/заголовков/кода
- `ColorTokens` — цвета текста, заголовков, ссылок, кода, цитат
- `SpacingTokens` — интервалы абзацев и заголовков
- `HeadingScaleTokens` — размеры уровней заголовков
- `PageDefaultsTokens` — размер страницы и опциональные поля
- `LinkPresentationTokens` — стиль подчёркивания гиперссылок
- `TablePresentationTokens` — значения по умолчанию для границ и выделения заголовков таблиц

## Встроенные темы

| Тема | Расположение | Назначение |
|-------|----------|---------|
| `DefaultTheme` | `styles/theme.py` | Производственное значение по умолчанию (Calibri, интервалы как в Word) |
| `AlternativeTestTheme` | `tests/themes/alternative_test_theme.py` | Проверка переключения тем только для тестов |

## Тема ≠ RenderContext

**Theme** отвечает на вопрос: какой это тип элемента документа (`Heading1`, `Quote`, `Normal`)?

**RenderContext** отвечает на вопрос: какое inline-форматирование активно (`bold`, `italic`)?

Пример: `# **Hello**` → стиль абзаца `Heading1` (тема) + run `bold=true` (RenderContext).

## Тема ≠ нумерация

Различие маркированных/нумерованных списков использует `NumberingManager` и `w:numPr`. Тема может настраивать только отступ/интервалы/шрифт `ListParagraph`.

## Тема ≠ макет таблицы

Сетка, colspan, rowspan и ширины ячеек остаются в движке таблиц. Тема предоставляет токены представления границ/заголовков, используемые OOXML-сборщиком таблиц.

## Тема ≠ секция

Тема задаёт размер страницы по умолчанию (и опциональные поля через `PageDefaultsTokens.emit_margins`). Явные директивы секций переопределяют через `SectionManager`.

## Приоритет

```text
Built-in default
    ↓
Theme
    ↓
Explicit document configuration
    ↓
Explicit section configuration
    ↓
Local inline formatting (RenderContext)
```

## Переключение тем

Один и тот же Markdown производит:

- **идентичный AST** (тема не влияет на парсинг)
- **идентичную семантическую структуру документа** (те же обработчики, те же роли `w:pStyle`)
- **разный `styles.xml`** (шрифты, размеры, цвета из токенов)

```python
from md2docx.pipeline import convert_markdown_to_docx
from md2docx.styles.theme import DefaultTheme
from tests.themes.alternative_test_theme import AlternativeTestTheme

convert_markdown_to_docx(source, out_a, theme=DefaultTheme.create())
convert_markdown_to_docx(source, out_b, theme=AlternativeTestTheme.create())
```

## Внешние темы (YAML)

Итерация 16 добавляет внешние YAML-темы через `ThemeLoader` и флаг CLI `--theme`.

```text
YAML
    ↓
ThemeLoader
    ↓
DocumentTheme
    ↓
ThemeResolver
    ↓
StyleRegistry
```

См. [`EXTERNAL_THEMES.md`](EXTERNAL_THEMES.md) для схемы YAML, правил валидации и примеров.

## Шаблоны DOCX

Итерация 17 добавляет шаблоны DOCX через `DocxPackageReader` и флаг CLI `--template`.

```text
Template DOCX
    ↓
TemplatePackage
    +
Markdown content fragment
    ↓
TemplateMerger
    ↓
Final DOCX
```

См. [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md). **Template ≠ Theme.**

## TODO

- **Caption** semantic style — реализовано (Iteration 20; курсив, 9pt; общий для подписей рисунков и таблиц)
- **`table_header` / `table_cell`** semantic styles — зарезервированы, не в реестре
- **Theme composition API** — базовый `compose_tokens()` существует; полное наследование TBD
- **Per-heading colors** — все заголовки сегодня используют общий `colors.heading`

См. также [`STYLE_SYSTEM.md`](STYLE_SYSTEM.md).
