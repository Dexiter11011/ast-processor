# Внешние темы документа (YAML)

Итерация 16 добавляет внешние YAML-темы и флаг CLI `--theme`.

## Архитектура

```text
YAML file
    ↓
ThemeLoader (safe_load + schema validation)
    ↓
DocumentTheme (YamlDocumentTheme)
    ↓
ThemeResolver
    ↓
StyleRegistry
    ↓
StylesXmlWriter
    ↓
word/styles.xml
```

YAML никогда не записывает OOXML напрямую. В схеме нет `raw_ooxml`, `xml` или произвольной карты стилей.

## Использование

```bash
md2docx README.md --theme examples/themes/corporate.yaml -o README.docx
```

Без `--theme` конвертер использует `DefaultTheme` точно так же, как раньше.

## Схема YAML (на основе токенов)

Внешние темы сопоставляются с группами [`ThemeTokens`](../src/md2docx/styles/tokens.py). Частичные файлы объединяются поверх `DefaultTheme`.

### Поля верхнего уровня

| Поле | Обязательно | Описание |
|-------|----------|-------------|
| `name` | no | Метка метаданных (по умолчанию: `unnamed`) |
| `typography` | no | Шрифты и размеры основного текста, заголовков и кода |
| `colors` | no | Цвета текста, заголовков, ссылок, кода, цитат |
| `spacing` | no | Интервалы абзацев, заголовков, списков, TOC |
| `headings` | no | Размеры шрифтов уровней заголовков |
| `page` | no | Размер страницы, ориентация, поля |
| `link` | no | Представление гиперссылок |
| `table` | no | Значения по умолчанию для границ/заголовков таблиц |

Неизвестные ключи на любом уровне отклоняются.

### Типографика

```yaml
typography:
  body:
    family: Arial
    size: 11pt
  heading:
    family: Arial
  code:
    family: Consolas
    size: 10pt
```

### Цвета

Шестизначный hex, с `#` или без:

```yaml
colors:
  text: "222222"
  heading: "123456"
  link: "0563C1"
  code: "333333"
  quote: "666666"
```

### Интервалы и заголовки

```yaml
spacing:
  paragraph_after: 6pt
  heading1_before: 12pt
  list_indent: 0.25in

headings:
  heading1: 28pt
  heading2: 20pt
  heading3: 16pt
```

Поддерживаемые единицы длины: `pt` (по умолчанию для чисел без единиц в spacing), `in`, `cm`, `mm`, `twips`.

Размеры шрифтов должны использовать `pt` (или голые числа, интерпретируемые как пункты).

### Параметры страницы по умолчанию

```yaml
page:
  size: A4          # or Letter, or {width: 21cm, height: 29.7cm}
  orientation: portrait
  emit_margins: true
  margins:
    top: 2cm
    right: 2cm
    bottom: 2cm
    left: 2cm
```

Явные директивы секций переопределяют значения страницы темы по умолчанию.

## На что влияет каждая группа токенов

| Группа токенов | Семантические стили / вывод |
|-------------|--------------------------|
| `typography` | Normal defaults, headings, code block, inline code |
| `colors` | Body text, heading runs, links, code, quotes |
| `spacing` | Normal, headings, lists, TOC levels |
| `headings` | Heading1/2/3 run sizes |
| `page` | Default section layout |
| `link` | Hyperlink underline |
| `table` | Table border/header presentation |

## Семантика слияния

Внешние темы — **частичные переопределения** поверх `DefaultTheme`:

1. Начать со встроенных токенов по умолчанию.
2. Для каждой присутствующей группы YAML объединить поле за полем в эту группу.
3. Передать объединённые токены в `ThemeResolver`.

Пример минимальной темы:

```yaml
name: minimal
colors:
  heading: "111111"
```

Все остальные свойства остаются из `DefaultTheme`.

## Тема ≠ другие системы

| Система | Связь |
|--------|--------------|
| `RenderContext` | Inline bold/italic/strike/code — без изменений от файла темы |
| `NumberingManager` | List numId/ilvl — не настраивается темой |
| Table layout | Grid/widths — не настраивается темой |
| Sections | Явный макет секции имеет приоритет над значениями страницы темы по умолчанию |

## Валидация и ошибки

- Missing file: `Error: theme file not found: path.yaml`
- Invalid YAML: `Error: invalid theme YAML: line N, column M`
- Schema: `Error: invalid theme: colors.heading must be a 6-digit hex color`
- Unknown key: `Error: invalid theme: typographi unknown theme field`

YAML загружается только через `yaml.safe_load`.

## Не поддерживается в этой итерации

- JSON theme files
- DOCX template themes
- Theme inheritance / discovery by name
- Per-style YAML maps (`styles.heading1.run.bold`)
- Raw OOXML injection
- `caption`, `table_header`, `table_cell` semantic styles (not in registry)
- Per-heading colors (all headings share `colors.heading`)

## Примеры

- [`examples/themes/corporate.yaml`](../examples/themes/corporate.yaml) — полный корпоративный пресет
- [`tests/fixtures/themes/minimal.yaml`](../tests/fixtures/themes/minimal.yaml) — переопределение одного цвета

См. также [`THEMES.md`](THEMES.md) для внутренней архитектуры тем.
