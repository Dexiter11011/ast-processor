# Пользовательская документация — Markdown → DOCX

Инструмент **md2docx** преобразует Markdown в корректный DOCX для технической документации MXDR: заголовки, таблицы, рисунки с подписями, оглавление, перекрёстные ссылки, поля Word и корпоративное оформление.

## Два режима работы

### 1. Прямая конвертация (один файл)

Подходит для новых документов, написанных в Markdown с нуля:

```bash
cd ast-processor
source .venv/bin/activate
md2docx document.md -o document.docx
```

### 2. Корпоративный pipeline (пакетная обработка)

Подходит для массовой переконвертации существующих DOCX из каталога `docx/fresh-data/`:

```bash
cd docx
python scripts/convert_pipeline.py
```

Pipeline выполняет roundtrip: DOCX → Markdown → обработка → DOCX с темой PT Sans.

## Быстрый старт — Hello World

Создайте файл `hello.md`:

```markdown
---
title: Hello World
author: Автор
---

<!-- header: title-field -->
<!-- footer: page-numbers -->

# Hello World

<!-- toc -->

Краткий пример **жирного** и *курсивного* текста.

## Раздел

- пункт 1;
- пункт 2.
```

Конвертация:

```bash
md2docx hello.md -o hello.docx --update-fields
```

Откройте `hello.docx` в Word и обновите поля (Ctrl+A → F9), чтобы появились оглавление и номера страниц.

## Разделы документации

| № | Файл | Содержание |
|---|------|------------|
| 01 | [Установка и запуск](01-ustanovka-i-zapusk.md) | Python, venv, CLI, флаги |
| 02 | [Основы Markdown](02-markdown-osnovy.md) | Заголовки, списки, ссылки, код |
| 03 | [Таблицы и рисунки](03-tablicy-i-risunki.md) | GFM-таблицы, директивы ячеек, изображения |
| 04 | [Навигация и оглавление](04-navigaciya-i-oglavlenie.md) | TOC, LOF, LOT, подписи, перекрёстные ссылки |
| 05 | [Поля и колонтитулы](05-polya-i-kolontituly.md) | Metadata, dynamic fields, header/footer |
| 06 | [Темы и шаблоны](06-temy-i-shablony.md) | `--theme`, `--template`, placeholders |
| 07 | [Корпоративный pipeline](07-korporativny-pipeline.md) | `convert_pipeline.py`, структура `docx/` |
| 08 | [Ограничения и FAQ](08-ogranicheniya-i-faq.md) | Что не поддерживается, типичные ошибки |

## Примеры и справочники

| Ресурс | Назначение |
|--------|------------|
| [`../ast-processor/tests/fixtures/`](../ast-processor/tests/fixtures/) | Рабочие примеры Markdown |
| [`../ast-processor/test/field/fields-demo.md`](../ast-processor/test/field/fields-demo.md) | Демонстрация полей и metadata |
| [`../ast-processor/tests/fixtures/navigation-dsl.md`](../ast-processor/tests/fixtures/navigation-dsl.md) | Навигация, подписи, refs |
| [`../themes/pt-sans.yaml`](../themes/pt-sans.yaml) | Корпоративная тема MXDR |

Подробная техническая документация для разработчиков — в [`../ast-processor/docs/`](../ast-processor/docs/).
