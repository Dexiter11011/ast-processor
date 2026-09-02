# 01 — Установка и запуск

## Требования

- **Python 3.9+**
- Для корпоративного pipeline дополнительно: **pandoc** (импорт DOCX → Markdown)

## Установка md2docx

Инструмент находится в каталоге [`ast-processor/`](../ast-processor/):

```bash
cd ast-processor
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
md2docx --help
md2docx --version
```

После установки команда `md2docx` доступна в активированном виртуальном окружении.

## Базовые команды

```bash
# Выходной файл рядом с исходником (document.docx)
md2docx document.md

# Явный путь выходного файла
md2docx document.md -o output.docx

# С корпоративной темой
md2docx document.md --theme ../docx/themes/pt-sans.yaml -o output.docx

# С проверкой OOXML после конвертации
md2docx document.md -o output.docx --validate

# Обновление полей при открытии в Word
md2docx document.md -o output.docx --update-fields
```

## Флаги CLI

| Флаг | Назначение |
|------|------------|
| `input.md` | Входной Markdown-файл (обязательный аргумент) |
| `-o`, `--output` | Путь к выходному DOCX (по умолчанию — имя входного файла с расширением `.docx`) |
| `--theme PATH` | Внешняя тема оформления (YAML) |
| `--template PATH` | DOCX-шаблон с колонтитулами и стилями Word |
| `--title TEXT` | Заголовок для placeholders шаблона и свойств документа |
| `--author TEXT` | Автор для placeholders и свойств документа |
| `--date TEXT` | Дата для placeholders шаблона (явное значение, не системная дата Word) |
| `--update-fields` | Word обновит dynamic fields при открытии документа |
| `--no-update-fields` | Не устанавливать автообновление полей |
| `--validate` | Проверить сгенерированный DOCX на корректность OOXML |
| `--version` | Показать версию md2docx |
| `--help` | Справка по командам |

## Примеры с шаблоном

```bash
md2docx README.md \
  --template examples/templates/corporate.docx \
  --title "Техническая документация" \
  --author "F6 Security" \
  --date "2026-08-31" \
  -o README.docx
```

Подробнее о темах и шаблонах — в [06-temy-i-shablony.md](06-temy-i-shablony.md).

## Коды возврата

| Код | Значение |
|-----|----------|
| `0` | Успешная конвертация |
| `1` | Ошибка аргументов (файл не найден и т.п.) |
| `2` | Ошибка конвертации (невалидный Markdown, шаблон, тема, изображение) |

Сообщения об ошибках выводятся в stderr:

```text
Error: input file does not exist: document.md
Error: image not found: logo.png
```

## Где искать примеры

| Каталог / файл | Содержание |
|----------------|------------|
| [`ast-processor/tests/fixtures/`](../ast-processor/tests/fixtures/) | Таблицы, навигация, списки, code blocks |
| [`ast-processor/test/field/fields-demo.md`](../ast-processor/test/field/fields-demo.md) | Поля, metadata, колонтитулы |
| [`ast-processor/examples/`](../ast-processor/examples/) | Шаблоны и темы для `--template` / `--theme` |

## Следующий шаг

Изучите [поддерживаемый синтаксис Markdown](02-markdown-osnovy.md) перед написанием документов.
