# Шаблоны DOCX

Итерация 17 добавляет внешние шаблоны DOCX и флаг CLI `--template`.

Итерация 18 добавляет скалярные плейсхолдеры шаблона и метаданные контекста документа.

Итерация 25 добавляет регионы навигации в шаблоне (`{{toc}}`, `{{list_of_figures}}`, `{{list_of_tables}}`). См. [`TEMPLATE_REGIONS.md`](TEMPLATE_REGIONS.md).

## Шаблон vs тема vs контекст документа

| Концепция | Роль |
|---------|------|
| **Template** | Базовый пакет DOCX (структура, стили Word, колонтитулы, секции, медиа) |
| **Theme** | Конфигурация визуальных токенов (YAML), влияющая на `styles.xml` |
| **DocumentContext** | Пользовательские/документные данные для плейсхолдеров и основных свойств |

Они разделены:

```text
Template          = physical DOCX structure
Theme             = visual configuration
DocumentContext   = title, author, date, subject, keywords
```

## Архитектура

```text
Template DOCX
    ↓
DocxPackageReader
    ↓
TemplatePackage
    +
Markdown → AST → DocumentFragment (OoxmlDocument.body_children)
    +
DocumentContext
    ↓
TemplateComposer (placeholder scan/validate/replace + insertion + remapping)
    ↓
Final DOCX package
```

Опциональный слой темы:

```text
Template styles.xml
    +
Theme styles (merge/override)
    ↓
Merged styles.xml
```

## Использование

```bash
md2docx README.md --template examples/templates/corporate.docx -o README.docx
```

С темой:

```bash
md2docx README.md \
  --template examples/templates/corporate.docx \
  --theme examples/themes/corporate.yaml \
  -o README.docx
```

С плейсхолдерами:

```bash
md2docx README.md \
  --template examples/templates/placeholders.docx \
  --title "Project Documentation" \
  --author "John Doe" \
  --date "2026-08-31" \
  -o README.docx
```

## Плейсхолдеры

Поддерживаемые плейсхолдеры в отдельном абзаце:

```text
{{content}}
{{toc}}
{{list_of_figures}}
{{list_of_tables}}
{{title}}
{{author}}
{{date}}
{{subject}}
{{keywords}}
```

Пример тела шаблона:

```text
Title:
{{title}}

Author:
{{author}}

Date:
{{date}}

{{content}}
```

Правила:

- Плейсхолдер должен быть единственным текстом в своём абзаце (разделённые runs допустимы)
- `{{content}}` должен встречаться ровно один раз
- Регионы навигации (`{{toc}}`, `{{list_of_figures}}`, `{{list_of_tables}}`) могут встречаться ноль или более раз
- Скалярные плейсхолдеры могут встречаться несколько раз (одно и то же значение)
- Неизвестные плейсхолдеры → ошибка
- Отсутствующие обязательные значения → ошибка
- Встроенные плейсхолдеры (`Project: {{title}}`) → ошибка
- Без выражений, фильтров и скриптов

## Контекст документа

Значения заполняются из:

1. Флагов CLI (`--title`, `--author`, `--date`) — наивысший приоритет
2. YAML front matter в Markdown — запасной вариант для title/author/subject/keywords

`{{date}}` требует явного значения `--date`. Движок не использует системные часы для дат в плейсхолдерах.

Основные свойства (`docProps/core.xml`) синхронизируются из того же контекста документа для title, author, subject и keywords.

## Точка вставки контента

Шаблоны должны содержать ровно **один отдельный абзац**:

```text
{{content}}
```

Пример:

```text
Introduction

{{content}}

Signature
```

Правила:

- Плейсхолдер должен быть единственным текстом в своём абзаце (разделённые runs допустимы)
- Отсутствующий плейсхолдер → ошибка
- Несколько плейсхолдеров `{{content}}` → ошибка
- Встроенный плейсхолдер (`Hello {{content}}`) → ошибка

## Приоритет

| Комбинация | Результат |
|-------------|--------|
| no template, no theme | DOCX по умолчанию с нуля (Iter 15 default) |
| template only | Пакет шаблона + вставленный контент; `styles.xml` шаблона |
| theme only | `styles.xml`, управляемый темой (Iter 16) |
| template + theme | Оболочка шаблона сохранена; тема объединяется со стилями шаблона |
| template + metadata flags | Плейсхолдеры заменены; core props обновлены при наличии title/author/subject/keywords |

Директивы секций/колонтитулов в Markdown **не поддерживаются** с `--template` (колонтитулы шаблона сохраняются).

## Сохранение пакета

Слияние сохраняет части шаблона, включая:

- `word/settings.xml`, `word/fontTable.xml`, `word/theme/*` (если присутствуют)
- Колонтитулы шаблона
- Медиа шаблона
- Неизвестные дополнительные части

Сгенерированный контент добавляет:

- Вставленные блоки тела в `{{content}}`
- Замену текста скалярных плейсхолдеров в теле шаблона
- Новые связи (переназначенные rIds)
- Новые медиа (с безопасными при коллизиях именами файлов)
- Объединённые определения нумерации (переназначенные numIds)
- Сгенерированные ID закладок переназначены выше максимального ID шаблона
- Сгенерированные **имена** закладок переназначены при коллизии (`architecture` → `architecture-1`); закладки шаблона сохранены

### Политика коллизий имён закладок

Когда сгенерированный контент содержит закладку с тем же именем, что и закладка шаблона:

1. Закладка шаблона сохраняет исходное имя
2. Сгенерированная закладка получает детерминированный суффикс (`-1`, `-2`, …)
3. Сгенерированные поля REF и внутренние гиперссылки во фрагменте переписываются на новое имя
4. Поля REF шаблона не изменяются

См. [`NAVIGATION.md`](NAVIGATION.md) для полной архитектуры навигации.

## Сборка фикстур шаблонов

```bash
PYTHONPATH=src python scripts/build-template-fixtures.py
```

Создаёт:

- `tests/fixtures/templates/minimal.docx`
- `tests/fixtures/templates/corporate.docx`
- `tests/fixtures/templates/corporate-navigation.docx` (TOC + LOF + LOT + `{{content}}`)
- `tests/fixtures/templates/navigation-collision.docx` (фикстура теста коллизии закладок)
- `tests/fixtures/templates/placeholders-basic.docx`
- `tests/fixtures/templates/placeholders-formatting.docx`
- `tests/fixtures/templates/regions-basic.docx`
- `tests/fixtures/templates/regions-navigation.docx`
- `tests/fixtures/templates/regions-complex.docx`
- `examples/templates/corporate.docx`
- `examples/templates/placeholders.docx`

См. также [`THEMES.md`](THEMES.md), [`EXTERNAL_THEMES.md`](EXTERNAL_THEMES.md), [`TEMPLATE_REGIONS.md`](TEMPLATE_REGIONS.md) и [`DYNAMIC_FIELDS.md`](DYNAMIC_FIELDS.md) для различия между статическими плейсхолдерами и динамическими полями Word.
