# 07 — Корпоративный pipeline

Скрипт [`convert_pipeline.py`](../scripts/convert_pipeline.py) выполняет пакетную переконвертацию корпоративных DOCX через Markdown с обогащением AST-директивами и темой PT Sans.

## Схема pipeline

```mermaid
flowchart LR
    FreshData["fresh-data/*.docx"]
    Pandoc["pandoc → intermediate MD"]
    PostProcess["post-process MD"]
    Md2docx["md2docx + pt-sans theme"]
    Output["docs/output/*.docx"]

    FreshData --> Pandoc --> PostProcess --> Md2docx --> Output
```

1. **Импорт** — pandoc конвертирует исходный DOCX в промежуточный Markdown
2. **Post-processing** — нормализация таблиц, списков, TOC, metadata
3. **Конвертация** — md2docx с темой `pt-sans.yaml` и флагами `--update-fields --validate`
4. **Результат** — DOCX в `docs/output/` + сводка `conversion-summary.md`

## Структура каталогов docx/

| Путь | Назначение |
|------|------------|
| `fresh-data/` | Исходные DOCX для обработки |
| `docs/intermediate/` | Промежуточный Markdown (выход pandoc) |
| `docs/markdown/` | Обработанный Markdown + assets |
| `docs/output/` | Итоговые DOCX + `conversion-summary.md` |
| `themes/pt-sans.yaml` | Корпоративная тема MXDR |
| `scripts/convert_pipeline.py` | Скрипт pipeline |

## Запуск

### Предусловия

1. Установлен md2docx в `ast-processor/.venv` (см. [раздел 01](01-ustanovka-i-zapusk.md))
2. Установлен **pandoc** (для шага импорта DOCX → MD)
3. В `fresh-data/` лежат исходные `.docx`

```bash
cd docx
python scripts/convert_pipeline.py
```

Скрипт обрабатывает все `*.docx` из `fresh-data/` и выводит прогресс в консоль:

```text
Processing document-ft.docx...
  OK → docs/output/document-ft.docx

Summary: docs/output/conversion-summary.md
```

## Типы документов

Pipeline определяет тип документа по имени файла и подставляет metadata автоматически:

| Префикс / тип | Subject | Keywords |
|---------------|---------|----------|
| `ft` | Функциональное тестирование | MXDR, функциональное тестирование, ФТ |
| `pmi` | Программа и методика испытаний | MXDR, ПМИ, испытания |
| `tt` | Техническое задание | MXDR, техническое задание, ТТ |
| `guide` | Руководство по безопасной настройке | MXDR, безопасная настройка, руководство |
| `plan` | План пилотного проекта | MXDR, пилотный проект, план |
| `bep` | Функциональные требования | BEP, функциональные требования |
| (прочие) | Техническая документация | MXDR, техническая документация |

## Post-processing

Pipeline автоматически выполняет:

| Шаг | Описание |
|-----|----------|
| HTML-таблицы → GFM | Конвертация `<table>` в Markdown-таблицы |
| HTML-изображения → `![alt](path)` | Нормализация путей к assets |
| Ручное TOC → `<!-- toc -->` | Удаление pandoc-оглавления, вставка Word TOC |
| Экранирование списков | `\`-item → нормальные Markdown-списки |
| Front matter | title, author, subject, keywords из DOCX и правил типа |
| Корпоративные директивы | header/footer, pagebreak, вводные разделы |
| Lint | Проверка через парсер md2docx; при ошибках — очистка HTML |

### Добавляемые директивы

Для каждого документа pipeline вставляет:

```markdown
<!-- header: title-field -->
<!-- header: author-field -->
<!-- header: date-field -->
<!-- footer: page-numbers -->

# {title}

<!-- toc -->
```

Для типов `ft`, `pmi`, `tt`, `bep` — раздел «Область применения»; для `guide` — «Назначение документа».

## Результат

После успешного запуска:

- DOCX-файлы — в `docs/output/`
- Обработанный Markdown — в `docs/markdown/` (можно править и конвертировать вручную)
- Сводка — `docs/output/conversion-summary.md`

Пример сводки:

| Source | Type | Title | Markdown | DOCX |
|--------|------|-------|----------|------|
| `document-ft.docx` | ft | Название | `docs/markdown/document-ft.md` | `docs/output/document-ft.docx` |

## Ручная доработка Markdown

После pipeline можно отредактировать файл в `docs/markdown/` и сконвертировать напрямую:

```bash
cd ast-processor
source .venv/bin/activate
md2docx ../docx/docs/markdown/document-ft.md \
  --theme ../docx/themes/pt-sans.yaml \
  -o ../docx/docs/output/document-ft.docx \
  --update-fields --validate
```

## Следующий раздел

[Ограничения и FAQ](08-ogranicheniya-i-faq.md) — типичные ошибки и чеклист проверки в Word.
