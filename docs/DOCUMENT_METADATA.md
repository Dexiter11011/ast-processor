# Метаданные документа

Единый поток метаданных документа для md2docx.

## Обзор

Все метаданные документа разрешаются в один канонический объект:

```text
CLI + front matter + defaults
        ↓
MetadataResolver
        ↓
ResolvedDocumentMetadata
        ├── {{title}}, {{author}}, {{date}}, {{subject}}, {{keywords}}
        ├── docProps/core.xml (dc:title, dc:creator, dc:subject, cp:keywords)
        └── TITLE / AUTHOR field cached display (Word reads core props at open)
```

## Приоритет источников

Для каждого поля побеждает источник с наивысшим приоритетом:

```text
CLI  >  front matter  >  defaults
```

Файлы шаблонов DOCX **не** задают значения метаданных по умолчанию. Существующие `docProps` шаблона сохраняются только когда не переданы разрешённые значения основных свойств.

## Поддерживаемые поля

| Поле | Front matter | CLI | Placeholder | Core property |
|-------|--------------|-----|-------------|---------------|
| title | yes | `--title` | `{{title}}` | `dc:title` |
| author | yes | `--author` | `{{author}}` | `dc:creator` |
| date | yes | `--date` | `{{date}}` | no (see below) |
| subject | yes | `--subject` | `{{subject}}` | `dc:subject` |
| keywords | yes | `--keywords` | `{{keywords}}` | `cp:keywords` |

Ключевые слова принимаются в виде значений через запятую во front matter или в CLI.

## Front matter (YAML)

```markdown
---
title: Project Documentation
author: Ivan Petrov
date: 2026-08-31
subject: Example
keywords: markdown, docx
---
```

Поддерживаемые ключи: `title`, `author`, `date`, `subject`, `keywords`.

Ключи конфигурации, такие как `theme:` и `template:`, парсером метаданных игнорируются.

Пустые значения или значения, состоящие только из пробелов, нормализуются в «не задано» (`None`).

## CLI

```bash
md2docx README.md \
  --title "Final Documentation" \
  --author "John Doe" \
  --date 2026-08-31 \
  --subject "Technical spec" \
  --keywords "markdown, docx" \
  -o README.docx
```

CLI переопределяет front matter независимо для каждого поля:

| Front matter | CLI | Result |
|--------------|-----|--------|
| title = A | `--title B` | title = B |
| author = Ivan | (none) | author = Ivan |

## Статическая дата vs поле Word DATE

| Механизм | Поведение |
|-----------|----------|
| `date` metadata / `{{date}}` | Статическое значение из CLI или front matter |
| Word `DATE` field | Динамическое; использует дату Word при обновлении поля |
| `dcterms:created` / `modified` | Временные метки пакета (явно в тестах; UTC now в production) |

Не следует рассматривать метаданные `date` как поле Word `DATE`.

## Динамические поля

| Поле | Разрешается из |
|-------|---------------|
| `TITLE` | `dc:title` в основных свойствах |
| `AUTHOR` | `dc:creator` в основных свойствах |
| `DATE` | Системная дата Word (не метаданные) |

Кэшированный текст отображения полей использует разрешённые title/author, когда они доступны.

## Архитектура

| Компонент | Ответственность |
|-----------|----------------|
| `MetadataResolver` | Приоритет, нормализация (без OOXML) |
| `ResolvedDocumentMetadata` | Каноническое разрешённое состояние |
| `DocumentContext` | Представление разрешённых метаданных для плейсхолдеров шаблона |
| `build_core_props_xml` | Сериализация разрешённых метаданных в OOXML |
| `TemplateComposer` | Замена плейсхолдеров (без логики приоритетов) |
| `CLI` | Сбор только сырых входных данных |

## Примеры

- [`examples/markdown/metadata.md`](../examples/markdown/metadata.md)
- [`tests/fixtures/metadata-full.md`](../tests/fixtures/metadata-full.md)

См. также [`DYNAMIC_FIELDS.md`](DYNAMIC_FIELDS.md) для директив полей.
