# Итерация 21 — Навигация по документу

Расширенный слой навигации по документу: семантические цели, переназначение закладок шаблона, усиление оглавления, списки рисунков / списки таблиц и типизированная проверка перекрёстных ссылок.

## Архитектура

```text
                         Document Navigation
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
           Heading             Figure               Table
              │                   │                   │
           Anchor              Anchor              Anchor
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         NavigationRegistry
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
             TOC             List of Figures     List of Tables
```

## Разделение ответственности

| Компонент | Ответственность | Не должен знать |
|-----------|-----------------|-----------------|
| `NavigationRegistry` | Семантические цели, порядок в документе, виды | Сырой XML, numId, rId |
| `BookmarkManager` | Создание/владение якорями (имя + id) | Семантику TOC, LOF, LOT |
| `ReferenceManager` | Разрешение цели → закладка; проверка вида | OOXML, Markdown |
| `FieldManager` | Рендеринг полей REF/TOC/SEQ/LOF/LOT | Markdown, семантику навигации |
| `TemplateMerger` | Инфраструктура переназначение ID и имён | Семантику Figure/Table |
| `SequenceManager` | Метки идентичности последовательности | Внутренности NavigationRegistry |

## NavigationRegistry

Хранит записи `NavigationTarget` в порядке документа:

```python
NavigationTarget(
    kind=NavigationTargetKind.FIGURE,
    name="architecture",           # logical slug
    bookmark_name="figure-architecture",
    label="Figure",
    level=None,                    # headings only
)
```

Точки регистрации:

- **Заголовки** — предварительное сканирование в `BookmarkManager.register_headings()` (также регистрируются в `NavigationRegistry`)
- **Рисунки / Таблицы** — регистрируются в `CaptionService._render_caption()` после создания закладки

## Политика имён закладок

| Вид | Шаблон | Пример |
|-----|--------|--------|
| Heading | `<slug>` | `architecture` |
| Figure | `figure-<slug>` | `figure-architecture` |
| Table | `table-<slug>` | `table-results` |

Номера последовательности **не** включаются в имена закладок. Нумерация выполняется на стороне Word через `SEQ Figure` / `SEQ Table`.

## Перемapping закладок шаблона

При слиянии сгенерированного содержимого в шаблон:

1. Собрать имена закладок шаблона из `word/document.xml`
2. Переназначить ID сгенерированных закладок (смещение выше максимального ID шаблона)
3. Для сгенерированных имён, конфликтующих с именами шаблона → переименовать с суффиксом `-1` (`architecture` → `architecture-1`)
4. Перезаписать только во фрагменте сгенерированного содержимого: `w:name`, REF `instrText`, `w:anchor` у гиперссылок
5. Закладки шаблона и поля REF шаблона остаются без изменений

Реализовано в `templates/bookmark_remap.py` через `BookmarkRemapMap`.

## ReferenceManager

Типизированная проверка перекрёстных ссылок:

```python
# OK — figure bookmark, figure kind
CrossReference(target="figure-architecture", kind=CaptionKind.FIGURE)

# Error — table bookmark referenced as figure
CrossReference(target="table-results", kind=CaptionKind.FIGURE)
# → ReferenceKindMismatchError
```

Ссылки на заголовки используют `kind=None` и `RefStyle.HEADING` (REF только с `\h`).

Ссылки на рисунки/таблицы используют `RefStyle.CAPTION` (REF с `\r \h`).

## TOC

Существующий семантический объект `TableOfContents` + поле Word:

```text
TOC \o "{min}-{max}" \h \z \u
```

Программный API:

```python
from md2docx.ast.types import TableOfContents, Document

Document(children=[TableOfContents(min_level=1, max_level=3), ...])
```

## Список рисунков / Список таблиц

Семантические узлы AST:

```python
from md2docx.ast.types import ListOfFigures, ListOfTables

Document(children=[
    ListOfFigures(),   # → TOC \h \z \c "Figure"
    ListOfTables(),    # → TOC \h \z \c "Table"
    ...
])
```

Word разрешает подписи динамически — статическая генерация списка в Python не выполняется.

## Программные фикстуры

Используйте `convert_ast_to_docx()` со сборщиками AST в `tests/navigation_fixtures.py` для тестов без синтаксиса Markdown.

## Проверка

- `validate_navigation()` — у каждой цели навигации есть якорь-закладка
- `ReferenceManager.validate_pending_refs()` — типизированная проверка REF в конце конвертации
- Валидатор пакета — уникальность закладок, цели REF, белый список полей TOC/LOF/LOT

## Связанные документы

- [FIGURES_AND_REFERENCES.md](FIGURES_AND_REFERENCES.md) — подписи, SEQ, REF
- [DYNAMIC_FIELDS.md](DYNAMIC_FIELDS.md) — типы полей и безопасность
- [DOCX_TEMPLATES.md](DOCX_TEMPLATES.md) — слияние шаблона и переназначение закладок
