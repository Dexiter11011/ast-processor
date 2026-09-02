# Ссылки и оглавление

Итерация 12 разделяет четыре связанных, но различных механизма навигации по документу.

## Четыре механизма

```text
Hyperlink     → jump to URL or in-document anchor
Bookmark      → named anchor inside the document
Cross-reference → pointer to an existing bookmark (internal links cover the primary case)
TOC           → Word field that builds a navigable outline on open
```

Их нельзя сводить к одной реализации.

## Внешние гиперссылки

Markdown:

```markdown
[OpenAI](https://openai.com)
```

Поток:

```text
Link AST
  → LinkHandler
  → RelationshipManager.add_external_hyperlink(url)
  → api.hyperlink(runs, rel_id=...)
  → w:hyperlink r:id="rIdN"
```

Одинаковые URL-цели используют один ID связи.

## Внутренние гиперссылки

Markdown:

```markdown
# Introduction

See [the intro](#introduction).
```

Поток:

```text
Heading AST
  → BookmarkManager (pre-scan slugs)
  → HeadingHandler
  → api.heading(..., bookmark_name, bookmark_id)
  → w:bookmarkStart / w:bookmarkEnd

Link AST (#introduction)
  → LinkHandler
  → BookmarkManager.resolve("introduction")
  → api.hyperlink(runs, anchor="introduction")
  → w:hyperlink w:anchor="introduction"   (no relationship)
```

Внутренние ссылки никогда не создают внешних связей.

## Закладки заголовков (включены по умолчанию)

Каждый заголовок получает детерминированный slug закладки, производный от его простого текста:

| Текст заголовка | Имя закладки |
|-----------------|--------------|
| Hello World | hello-world |
| API Reference! | api-reference |
| Introduction (×3) | introduction, introduction-1, introduction-2 |

Правила slug (`references/slug.py`):

- Нижний регистр, нормализация NFKD, пунктуация → дефисы
- Буквы и цифры Unicode сохраняются после нормализации
- Пустой slug → `section`
- Дубликаты slug получают числовые суффиксы

Форматирование внутри заголовков игнорируется для текста slug (в стиле GitHub).

## Битые внутренние ссылки

```markdown
[Missing](#does-not-exist)
```

Когда закладка не зарегистрирована:

- Гиперссылка не создаётся
- Текст ссылки рендерится как обычные inline runs
- Проверка пакета может пометить неразрешённые якоря, если они были созданы

Отсутствующие закладки никогда не создаются молча.

## Оглавление

Вставка через HTML-комментарий-директиву (тот же шаблон, что у разрывов страниц/секций):

```markdown
<!-- toc -->
<!-- toc: 2-3 -->
```

Создаёт сложное поле Word:

```text
w:fldChar begin → w:instrText TOC \o "1-3" \h \z \u → w:fldChar separate → w:fldChar end
```

Word обновляет видимое оглавление при открытии документа. Генератор не рендерит статический нумерованный список.

Стили TOC `TOC1`, `TOC2`, `TOC3` регистрируются в Style System.

## Владение

| Задача | Владелец |
|--------|----------|
| Связи с внешними URL | `RelationshipManager` |
| ID закладок и реестр slug | `BookmarkManager` |
| Инструкция поля TOC | `TocManager` |
| Генерация OOXML | `md2docx.ooxml.api` |

Обработчики не должны писать сырой XML `w:hyperlink`, `w:bookmarkStart`, `w:bookmarkEnd` или полей.

## Компоненты

```text
src/md2docx/references/   Bookmark, BookmarkManager, slug, validator
src/md2docx/toc/          TocSpec, TocManager
src/md2docx/ooxml/bookmark.py
src/md2docx/ooxml/field.py
src/md2docx/elements/toc.py
```

## Тесты

- `tests/references/` — модульные тесты slug и BookmarkManager
- `tests/ooxml/test_bookmark.py`, `test_toc_field.py`
- `tests/integration/test_hyperlinks_docx.py`, `test_bookmarks_docx.py`, `test_toc_docx.py`
- Golden-фикстуры: `external-links`, `internal-links`, `bookmarks`, `toc`, `references-integration`, …
