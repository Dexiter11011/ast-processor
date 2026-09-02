# Iteration 28 — Аудит фазы 1

Read-only аудит, проверенный по кодовой базе после Iteration 27 (690 pytest, 70 architecture, 62 golden, validate-docx PASS).

## Существующие семантические абстракции

| Слой | Модуль | Примечания |
|------|--------|------------|
| Markdown AST | `md2docx.ast.types` | Неизменяемые dataclass для блочных и inline-узлов |
| Модели подписей | `md2docx.captions.model` | `Figure`, `TableWithCaption`, `CrossReferenceBlock` (использует внутренний AST) |
| Inline-состояние | `md2docx.processor.inline_formatting` | `InlineFormatting`, `RenderContext` |
| Роли стилей | `md2docx.styles.semantic` | Семантические константы, разрешаемые через `StyleManager` |
| Метаданные | `md2docx.metadata.resolved` | Неизменяемый `ResolvedDocumentMetadata` |
| OOXML-фасад | `md2docx.ooxml.api` | ~40 функций, возвращающих элементы `lxml` |
| Аккумулятор документа | `md2docx.ooxml.document` | `OoxmlDocument.body_children` — де-факто фрагмент содержимого |

## Существующая модель фрагмента

- Класса `DocumentFragment` или `RichDocumentFragment` не существует.
- Внутренне «фрагмент» означает `list[lxml.etree._Element]`.
- Регионы шаблона плагинов: `FragmentRenderer = Callable[[ProcessingContext], list[Element]]`.
- Встроенные обработчики возвращают `None` и мутируют `ProcessingContext`.

## Существующая модель композиции

- Блоки добавляются в `OoxmlDocument.body_children`.
- Inline-содержимое использует `run_collector` во время рекурсии обработчиков.
- Pipeline шаблонов склеивает фрагменты через `TemplateCompositionPlan` и переназначает ID в `TemplateMerger`.

## Безопасные публичные кандидаты

Стилизованные абзацы с rich inline, разрывы строк, валидированные гиперссылки, поля из белого списка, изображения path/bytes, списки (numId принадлежит NumberingManager), метаданные только для чтения, композиция фрагментов.

## Небезопасные внутренние части

Импорты `md2docx.ast.*`, `ProcessingContext`/`AstProcessor`, коллекторы, сырой lxml, назначение numId/rId, произвольные инструкции полей, прямой доступ к пакету.

## Пробелы

Плагины должны собирать OOXML через Tier B `ooxml.api`; нет API inline-композиции; закладки/поля/медиа/списки/подписи требуют недокументированных менеджеров.

## Рекомендуемый Rich Semantic API

Новый модуль Tier B `md2docx.semantic` с неизменяемыми семантическими типами значений, фасадом `SemanticContext`, внутренним адаптером `SemanticRenderer`. Обработчики могут возвращать `RichDocumentFragment` (обратно совместимо с void/OOXML-путями). Таблицы отложены в v1.
