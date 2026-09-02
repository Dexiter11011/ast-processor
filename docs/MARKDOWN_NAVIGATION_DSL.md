# DSL навигации в Markdown

Канонические HTML-комментарии-директивы для оглавления, списков рисунков/таблиц, подписей и перекрёстных ссылок.

## Обзор

Функции навигации используют **отдельные HTML-комментарии** на собственной строке (тот же шаблон, что у `<!-- toc -->`, `<!-- pagebreak -->` и директив полей). Парсер выдаёт промежуточные маркеры; `caption_transform` объединяет их в семантические узлы AST (`Figure`, `TableWithCaption`, `CrossReferenceBlock`, `ListOfFigures`, `ListOfTables`).

```text
Markdown → pre-scan directives → markdown-it → caption_transform → AstProcessor → DOCX
```

## Оглавление и списки

```markdown
<!-- toc -->
<!-- toc: 2-3 -->
<!-- lof -->
<!-- lot -->
```

| Директива | Узел AST | Поле Word |
|-----------|----------|-----------|
| `<!-- toc -->` | `TableOfContents` (уровни 1–3) | `TOC \o "1-3"` |
| `<!-- toc: 2-3 -->` | `TableOfContents` | `TOC \o "2-3"` |
| `<!-- lof -->` | `ListOfFigures` | `TOC \c "Figure"` |
| `<!-- lot -->` | `ListOfTables` | `TOC \c "Table"` |

Размещайте директивы после YAML front matter и перед основным телом. Обновите поля в Word с помощью **Ctrl+A → F9**.

## Подписи к рисункам

Директива подписи должна непосредственно следовать за отдельной строкой с изображением:

```markdown
![Architecture overview](architecture.png)

<!-- caption: figure Architecture overview -->
```

Создаёт нумерованную подпись к рисунку и закладку `figure-architecture-overview`.

## Подписи к таблицам

Директива подписи должна непосредственно предшествовать GFM-таблице:

```markdown
<!-- caption: table Configuration values -->

| Name | Value |
|------|-------|
| A    | 1     |
```

Создаёт закладку `table-configuration-values`.

## Перекрёстные ссылки (блок)

Ссылка на рисунок или таблицу по логическому slug:

```markdown
<!-- ref: figure architecture-overview -->
<!-- ref: figure architecture-overview prefix="See " -->
<!-- ref: table configuration-values prefix="See " -->
```

| Часть | Значение |
|-------|----------|
| `figure` / `table` | Вид цели |
| slug | Логический id закладки (см. ниже) |
| `prefix="..."` | Текст перед номером ссылки (по умолчанию: `"See "`) |

### Нормализация slug

Текст подписи преобразуется в slug для имени закладки через `caption_bookmark_name()`:

| Текст подписи | Закладка |
|---------------|----------|
| `Architecture overview` | `figure-architecture-overview` |
| `Configuration values` | `table-configuration-values` |

В `<!-- ref: ... -->` можно использовать логический slug (`architecture-overview`) или полное имя закладки (`figure-architecture-overview`).

Поддерживаются ссылки вперёд: `<!-- ref: ... -->` может появиться до подписи, на которую ссылается.

## Ссылки на заголовки (существующий синтаксис)

Ссылки на заголовки **не** используют DSL навигации:

```markdown
[See Architecture](#architecture)

<!-- field: ref architecture -->
```

Они разрешаются в закладки заголовков, а не в подписи рисунков/таблиц.

## Ограничения (Итерация 22)

| Тема | Статус |
|------|--------|
| Текст подписи | Только простая строка внутри HTML-комментария |
| Rich markdown в подписях (`**bold**`) | Не поддерживается |
| Атрибут `title` у изображения | Не считается подписью |
| Блоки `::: figure` в ограждении | Не поддерживаются |
| Inline `@figure[slug]` | Не поддерживается |
| Inline-изображения в абзацах | Не преобразуются в `Figure` (только отдельные строки `![...](...)`) |

## Ошибки

| Сообщение | Причина |
|-----------|---------|
| `figure caption directive must immediately follow an image` | Подпись к рисунку без изображения или в неверном месте |
| `table caption directive must be immediately followed by a table` | Подпись к таблице без таблицы или в неверном месте |
| `Error at line N: ...` | CLI указывает путь к файлу и строку, если доступно |

## Примеры

- Руководство пользователя (на русском): [`docs/user-docs/04-navigaciya-i-oglavlenie.md`](user-docs/04-navigaciya-i-oglavlenie.md)
- Запускаемый пример: [`examples/markdown/navigation.md`](../examples/markdown/navigation.md)
- Тестовая фикстура: [`tests/fixtures/markdown/navigation/navigation-dsl.md`](../tests/fixtures/markdown/navigation/navigation-dsl.md)
