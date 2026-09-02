# 05 — Поля и колонтитулы

md2docx поддерживает три связанных, но разных механизма metadata и полей Word.

## Три механизма

| Механизм | Пример | Поведение |
|----------|--------|-----------|
| YAML front matter | `title: ...` | Свойства документа (`docProps/core.xml`) |
| Placeholders шаблона | `{{title}}` | Статическая подстановка при merge с `--template` |
| Dynamic fields | `<!-- field: date -->` | Word пересчитывает при открытии |

## YAML front matter

```markdown
---
title: Техническое задание MXDR
author: F6 Security
subject: MXDR — техническое задание
keywords: MXDR, ТТ, безопасность
---
```

Значения попадают в свойства документа и доступны полям TITLE, AUTHOR и т.д.

## Колонтитулы

Директивы задают содержимое header/footer для текущей секции документа:

```markdown
<!-- header: title-field -->
<!-- header: author-field -->
<!-- header: date-field -->
<!-- footer: page-numbers -->
```

| Директива | Поле Word | Содержание |
|-----------|-----------|------------|
| `<!-- header: title-field -->` | TITLE | Заголовок из свойств документа |
| `<!-- header: author-field -->` | AUTHOR | Автор из `dc:creator` |
| `<!-- header: date-field -->` | DATE | Текущая дата (Word, не `--date`) |
| `<!-- footer: page-numbers -->` | PAGE + NUMPAGES | «Страница N из M» |

Разместите директивы **до** основного содержимого, сразу после front matter.

> **Важно:** при использовании `--template` директивы header/footer в Markdown **не поддерживаются** — сохраняются колонтитулы из шаблона. Подробнее в [06-temy-i-shablony.md](06-temy-i-shablony.md).

## Dynamic fields в теле документа

```markdown
<!-- field: date -->

<!-- field: ref ref-target-section -->

<!-- field: seq Figure -->
```

| Директива | Поле | Назначение |
|-----------|------|------------|
| `<!-- field: date -->` | DATE | Дата в абзаце |
| `<!-- field: ref <bookmark> -->` | REF | Ссылка на bookmark заголовка |
| `<!-- field: seq Figure -->` | SEQ | Нумерация последовательности (без caption DSL) |
| `<!-- toc -->` | TOC | Оглавление (см. [раздел 04](04-navigaciya-i-oglavlenie.md)) |

### REF на заголовок vs REF на рисунок

| Механизм | Markdown | Цель |
|----------|----------|------|
| REF на заголовок | `<!-- field: ref slug -->` | Bookmark заголовка |
| REF на рисунок/таблицу | `<!-- ref: figure slug -->` | Caption bookmark |

## Разрывы страниц и секции

```markdown
<!-- pagebreak -->

<!-- section: landscape -->
```

| Директива | Эффект |
|-----------|--------|
| `<!-- pagebreak -->` | Разрыв страницы без смены параметров секции |
| `<!-- section: a4 -->` | Новая секция A4 portrait |
| `<!-- section: letter -->` | Letter portrait |
| `<!-- section: landscape -->` | A4 landscape |
| `<!-- section: a4 margins=720,720,720,720 -->` | A4 с кастомными полями (twips) |

Разрыв секции меняет ориентацию, размер страницы и может задать отдельные колонтитулы.

## Полный пример

Живой демо-файл: [`fields-demo.md`](../ast-processor/test/field/fields-demo.md).

```markdown
---
title: Fields & Metadata Demo
author: Ivan Ivanov
subject: Demonstration of Word fields
keywords: fields, metadata, md2docx
---

<!-- header: title-field -->
<!-- header: author-field -->
<!-- header: date-field -->
<!-- footer: page-numbers -->

# Fields & Metadata Demo

<!-- toc -->

Текущая дата: <!-- field: date -->

## Ref Target Section

<!-- field: ref ref-target-section -->
```

Откройте сгенерированный DOCX в Word и обновите поля (Ctrl+A → F9).

## CLI и metadata

```bash
md2docx document.md \
  --title "Заголовок" \
  --author "Автор" \
  --date "2026-08-31" \
  -o output.docx \
  --update-fields
```

| Флаг | Куда попадает |
|------|---------------|
| `--title` | Placeholders `{{title}}`, `dc:title`, поле TITLE |
| `--author` | Placeholders `{{author}}`, `dc:creator`, поле AUTHOR |
| `--date` | Только placeholders `{{date}}` (не поле DATE Word) |

## Следующий раздел

[Темы и шаблоны](06-temy-i-shablony.md) — визуальное оформление и корпоративные DOCX-шаблоны.
