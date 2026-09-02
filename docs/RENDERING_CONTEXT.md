# Контекст рендеринга

Итерация 8 вводит явную модель рендеринга для inline-преобразования Markdown → OOXML.

## Проблема

Ранее `StrongHandler` и `EmphasisHandler` собирали вложенные runs и применяли `api.bold()` / `api.italic()` **после** создания run. Форматирование жило неявно в готовых элементах `w:rPr`, а не в типизированном состоянии контекста.

## Модель

Два неизменяемых dataclass в `processor/inline_formatting.py`:

- **`InlineFormatting`** — `{ bold, italic, code }` с `with_bold()`, `with_italic()`, `with_code()`
- **`RenderContext`** — оборачивает `InlineFormatting`; `derive()` создаёт дочерний контекст без изменения родителя

`ProcessingContext.render_context` хранит текущее состояние. Обработчики используют `push_render_context()` для ограничения форматирования поддеревьями AST.

## Правила обработчиков

| Handler | Поведение |
|---------|----------|
| `TextHandler` | `api.run_from_formatting(text, context.render_context.formatting)` |
| `StrongHandler` | Derive `with_bold()`, process children |
| `EmphasisHandler` | Derive `with_italic()`, process children |
| `InlineCodeHandler` | Derive `with_code()`, resolve Code character style |
| `LinkHandler` | Same render context for children; one external rel via `RelationshipManager` |

Strong/Emphasis **не должны** вызывать `api.bold()` / `api.italic()` напрямую.

## Слой OOXML

`ooxml/run_format.py`:

- `run_from_formatting(text, formatting, *, r_style="")` — build `w:r` at emission time
- `apply_inline_formatting(run, formatting, *, r_style="")` — apply state to existing run

`api.run_from_formatting` — точка входа для обработчиков.

## Нецели (эта итерация)

- Слияние / coalescing соседних runs с одинаковым форматированием
- Новые возможности Markdown
- Изменения `AstProcessor`, парсера или типов AST

## Тесты

- `tests/processor/test_render_context.py` — unit-тесты derive/isolation
- `tests/elements/test_formatting_leakage.py` — bold/italic не должны протекать между соседними узлами
- `tests/fixtures/inline-formatting-matrix.md` — исчерпывающий inline-fixture
- `tests/architecture/test_layer_boundaries.py` — handlers не должны вызывать `api.bold`/`api.italic`

## Связанные материалы

Стили уровня документа (Heading1, Quote, Normal) обрабатываются **системой стилей** — см. [`STYLE_SYSTEM.md`](STYLE_SYSTEM.md). Render Context охватывает только inline-форматирование.
