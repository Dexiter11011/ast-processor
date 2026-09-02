# 06 — Темы и шаблоны

md2docx разделяет **структуру документа** (шаблон), **визуальное оформление** (тема) и **данные документа** (metadata).

## Три понятия

| Понятие | Роль |
|---------|------|
| **Template** (`--template`) | Базовый DOCX: стили Word, колонтитулы, секции, медиа |
| **Theme** (`--theme`) | YAML-конфигурация шрифтов, цветов, отступов → `styles.xml` |
| **DocumentContext** | title, author, date, subject, keywords |

```text
Template     = физическая структура DOCX
Theme        = визуальная конфигурация
DocumentContext = данные для placeholders и свойств
```

## Тема (--theme)

Тема задаётся YAML-файлом. Корпоративная тема MXDR:

[`../themes/pt-sans.yaml`](../themes/pt-sans.yaml)

```yaml
name: pt-sans

typography:
  body:
    family: "PT Sans"
    size: 12pt
  heading:
    family: "PT Sans"
  code:
    family: Consolas
    size: 10pt

colors:
  text: "000000"
  heading: "000000"
  link: "0563C1"

page:
  size: A4
  orientation: portrait
  margins:
    top: 2cm
    right: 2cm
    bottom: 2cm
    left: 2.5cm
```

### Команда с темой

```bash
md2docx document.md \
  --theme ../docx/themes/pt-sans.yaml \
  -o document.docx
```

Тема влияет на шрифты, размеры заголовков, цвета ссылок, поля страницы. Без `--theme` используется встроенная тема по умолчанию (Calibri).

## Шаблон (--template)

Шаблон — готовый DOCX с оформлением компании. Markdown-контент вставляется в placeholder `{{content}}`.

```bash
md2docx README.md \
  --template examples/templates/corporate.docx \
  -o README.docx
```

### Placeholders шаблона

| Placeholder | Источник |
|-------------|----------|
| `{{content}}` | Тело Markdown (обязательный) |
| `{{title}}` | `--title` или YAML `title` |
| `{{author}}` | `--author` или YAML `author` |
| `{{date}}` | `--date` (явное значение) |

```bash
md2docx README.md \
  --template examples/templates/placeholders.docx \
  --title "Техническая документация" \
  --author "F6 Security" \
  --date "2026-08-31" \
  -o README.docx
```

### Тема + шаблон вместе

```bash
md2docx README.md \
  --template examples/templates/corporate.docx \
  --theme examples/themes/corporate.yaml \
  -o README.docx
```

Тема переопределяет/дополняет стили из `styles.xml` шаблона.

## Ограничение: template vs header/footer directives

При `--template` директивы колонтитулов в Markdown **игнорируются**:

```markdown
<!-- header: title-field -->   ← не работает с --template
<!-- footer: page-numbers -->   ← не работает с --template
```

Используйте колонтитулы, уже заданные в DOCX-шаблоне.

Без `--template` колонтитулы задаются директивами из [раздела 05](05-polya-i-kolontituly.md).

## Где взять шаблоны и темы

| Каталог | Содержание |
|---------|------------|
| [`ast-processor/examples/templates/`](../ast-processor/examples/templates/) | Примеры DOCX-шаблонов |
| [`ast-processor/examples/themes/`](../ast-processor/examples/themes/) | Примеры YAML-тем |
| [`docx/themes/`](../themes/) | Корпоративные темы MXDR |

## Следующий раздел

[Корпоративный pipeline](07-korporativny-pipeline.md) — автоматическая обработка пакета документов MXDR.
