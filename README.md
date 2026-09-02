# md2docx

Автономный CLI, который конвертирует Markdown в DOCX через явный конвейер **AST → OOXML**.

Инструмент собирает настоящий пакет Office Open XML — `document.xml`, `styles.xml`, `numbering.xml`, relationships, media и `[Content_Types].xml` — без делегирования генерации документа чёрному ящику DOCX-библиотеки.

## Что делает

1. Читает Markdown-файл (опциональный YAML front matter для метаданных).
2. Парсит Markdown в типизированное **AST** (Abstract Syntax Tree).
3. Обходит AST одним **AstProcessor**, направляя каждый узел в dedicated **element handler**.
4. Handlers вызывают слой **OOXML** для построения элементов WordprocessingML.
5. Собирает валидный **DOCX** (ZIP-архив с XML-частями и медиа).

Поддерживаются абзацы, заголовки, жирный/курсив, inline-код, ссылки, списки, цитаты, горизонтальные линии, блоки кода, изображения и таблицы (с директивами форматирования).

## Установка

```bash
cd ast-processor
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Требуется **Python 3.9+**.

## Запуск

```bash
md2docx input.md                  # пишет input.docx рядом с исходником
md2docx input.md -o output.docx   # явный путь вывода
md2docx input.md -o output.docx --validate   # конвертация и валидация OOXML-пакета
md2docx README.md \
  --title "Final Documentation" \
  --author "John Doe" \
  --date 2026-08-31 \
  -o README.docx                  # CLI перекрывает YAML front matter (по полям)
md2docx --help
md2docx --version
```

Метаданные документа (title, author, date, subject, keywords) собираются из CLI и YAML front matter в единую модель для плейсхолдеров шаблона, core properties и динамических полей. См. [`docs/DOCUMENT_METADATA.md`](docs/DOCUMENT_METADATA.md).

Ошибки печатаются в stderr (см. [`docs/ERROR_HANDLING.md`](docs/ERROR_HANDLING.md)):

```text
Error: input file does not exist: document.md
Error: unsupported AST node: footnote
```

Флаг `--debug` выводит полный traceback для неожиданных внутренних ошибок. С `--validate` невалидный вывод обнаруживается до замены финального файла, поэтому существующий output сохраняется при ошибке валидации.

## Архитектура

Слои строго разделены. У каждого слоя одна задача — он не должен протекать в соседние.

```text
┌─────────────────────────────────────────────────────────────┐
│  CLI (cli/)           разбор аргументов, коды выхода        │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Parser (parser/)     Markdown → AST                        │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  AST (ast/)           типизированные определения узлов      │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Processor (processor/)                                       │
│    AstProcessor       один обход дерева, диспетчеризация      │
│    HandlerRegistry    type → handler                          │
│    ProcessingContext  общий document, rels, styles, media     │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  Elements (elements/)  один handler на элемент Markdown       │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│  OOXML (ooxml/)       builders WordprocessingML + API         │
│    api.py             фасад для handlers                      │
│    xml_builder.py     безопасная сериализация lxml            │
│    package.py         сборка DOCX ZIP (нижний слой OOXML)     │
└─────────────────────────────────────────────────────────────┘
```

| Слой | Расположение | Ответственность |
|------|--------------|-----------------|
| CLI | `src/md2docx/cli/` | Пользовательский интерфейс, сообщения об ошибках |
| Parser | `src/md2docx/parser/` | Markdown → AST (без OOXML) |
| AST | `src/md2docx/ast/` | Типизированные dataclass-узлы |
| Processor | `src/md2docx/processor/` | Обход AST, registry, общий контекст |
| Elements | `src/md2docx/elements/` | Один handler на тип элемента |
| OOXML | `src/md2docx/ooxml/` | Генерация XML, пакет DOCX |

**Правило:** Markdown, AST, Processing, OOXML и ZIP не должны смешиваться в одном модуле.

## Что такое AST?

AST — дерево обычных Python dataclasses в `src/md2docx/ast/types.py`. У каждого узла есть дискриминатор `type` (строка) и поля, специфичные для конструкции.

Пример — Markdown `Hello **world**` становится:

```text
Document
└── Paragraph
    ├── Text("Hello ")
    └── Strong
        └── Text("world")
```

Блочные узлы (`Paragraph`, `Heading`, `List`, `Table`, …) находятся на уровне документа. Inline-узлы (`Text`, `Strong`, `Link`, …) живут внутри блочных. Парсер создаёт AST; handlers его потребляют. AST ничего не знает про OOXML или Word.

## Как AST становится OOXML

Сквозной поток (`pipeline.py`):

```text
Markdown file
    → MarkdownParser.parse()          # слой parser
    → Document AST
    → ProcessingContext.create_default()
    → AstProcessor(registry).process_document(ast, context)
         for each node:
           handler = registry.get(node.type)
           handler.process(node, context, processor)
    → OoxmlDocument (накопленные w:p, w:tbl, … в памяти)
    → DocxPackageWriter.write_from_context()   # ZIP + все XML-части
    → output.docx
```

**AstProcessor** — тонкий диспетчер: сам XML он не строит:

```python
handler = registry.get(node.type)   # raises UnsupportedNodeError if missing
handler.process(node, context, processor)
```

Handlers производят OOXML двумя путями:

- **Inline-контент** — добавляют runs в `context.run_collector`, затем родительский handler (например, `ParagraphHandler`) сбрасывает их в абзац.
- **Блочный контент** — вызывают `context.document.add_*()`, которые добавляют элементы уровня body.

Весь XML строится через **lxml** в `ooxml/xml_builder.py`. Пользовательский текст никогда не конкатенируется в строки тегов; экранирование делает сериализатор.

После обработки `DocxPackageWriter` оборачивает body в `word/document.xml`, добавляет `styles.xml`, опциональный `numbering.xml`, файлы relationships, media-части и `[Content_Types].xml`, затем пишет ZIP.

## Контекст рендеринга

Inline-форматирование (жирный, курсив, inline-код) проходит через явный **RenderContext**, а не через постфактум-мутацию runs.

```text
AST inline node
    → InlineHandler (Strong, Emphasis, …)
    → RenderContext.derive()          # push child formatting state
    → AstProcessor.process_children()
    → TextHandler
    → api.run_from_formatting(text, InlineFormatting)
    → apply_inline_formatting → w:rPr (w:b, w:i, w:rStyle)
```

`ProcessingContext` несёт и временные коллекторы, и состояние рендеринга:

```text
ProcessingContext
├── document, relationships, styles, numbering, media   (общая инфраструктура)
├── run_collector                                       (накопление inline runs)
└── render_context: RenderContext
      └── formatting: InlineFormatting { bold, italic, code }
```

**Пример трассы** — Markdown `**bold *italic***`:

```text
StrongHandler   → derive(bold=True)
  EmphasisHandler → derive(bold=True, italic=True)
    TextHandler   → run_from_formatting("italic", bold=True, italic=True)
```

ID relationships для гиперссылок остаются в `RelationshipManager` — никогда в `InlineFormatting`.

Полное архитектурное описание: [`docs/RENDERING_CONTEXT.md`](docs/RENDERING_CONTEXT.md).

## Система стилей

Презентация на уровне документа (заголовки, цитаты, блоки кода, списки) идёт через **StyleRegistry** на основе неизменяемых объектов **StyleDefinition**.

```text
AST block node
    → Handler выбирает семантическую роль (heading1, quote, normal, …)
    → StyleManager.to_ooxml(semantic_id)
    → document.xml w:pStyle / w:rStyle
    → StylesXmlWriter(registry) → word/styles.xml
```

**Style System** (paragraph/character styles) и **Render Context** (inline bold/italic/code) разделены:

```text
# **Hello**  →  pStyle=Heading1  +  run bold=true
```

См. [`docs/STYLE_SYSTEM.md`](docs/STYLE_SYSTEM.md), [`docs/LISTS_AND_TABLES.md`](docs/LISTS_AND_TABLES.md) и [`docs/SECTIONS_AND_LAYOUT.md`](docs/SECTIONS_AND_LAYOUT.md).

## Как добавить новый элемент Markdown

Добавление элемента — **локальное изменение** по слоям. Переписывать `AstProcessor` **не нужно**.

Ниже полный набросок для сносок (`[^1]`). Адаптируйте имена и детали OOXML под свою спецификацию.

### Шаг 1 — тип AST (`ast/types.py`)

```python
@dataclass
class Footnote:
    type: Literal["footnote"] = "footnote"
    id: str = ""
    children: list[InlineNode] = field(default_factory=list)
```

Добавьте `Footnote` в union `InlineNode` (или `BlockNode`).

### Шаг 2 — Parser (`parser/markdown_parser.py`)

Расширьте обход токенов markdown-it, чтобы эмитить узлы `Footnote` при встрече синтаксиса сносок. Код парсера не должен импортировать handlers или OOXML.

### Шаг 3 — Handler (`elements/footnote.py`)

```python
from md2docx.ast.types import Footnote
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class FootnoteHandler:
    def process(
        self,
        node: Footnote,
        context: ProcessingContext,
        processor: AstProcessor,
    ) -> None:
        processor.process_children(node, context)
        runs = list(context.run_collector)
        context.run_collector.clear()
        context.run_collector.append(api.footnote_run(runs, footnote_id=node.id))
```

Handlers используют только **`md2docx.ooxml.api`** — не низкоуровневые builder-модули напрямую.

### Шаг 4 — OOXML (`ooxml/footnote.py` + `ooxml/api.py`)

Реализуйте WordprocessingML для сносок в слое OOXML:

```python
# ooxml/footnote.py — внутренний builder через xml_builder.element()
def build_footnote_run(children: list[Element], *, footnote_id: str) -> Element:
    ...

# ooxml/api.py — фасад для handlers
def footnote_run(runs: list[Element], *, footnote_id: str) -> Element:
    return build_footnote_run(runs, footnote_id=footnote_id)
```

Если сноскам нужна новая часть пакета (`footnotes.xml`), расширьте `RelationshipManager`, `content_types.py` и `DocxPackageWriter` — по-прежнему не трогая processor.

### Шаг 5 — Регистрация handler (`elements/__init__.py`)

```python
from md2docx.elements.footnote import FootnoteHandler

def create_default_registry() -> HandlerRegistry:
    return (
        HandlerRegistry()
        # … существующие handlers …
        .register("footnote", FootnoteHandler())
    )
```

Это единственное «протягивание» проводки вне новых файлов. `AstProcessor` остаётся без изменений.

### Шаг 6 — Тесты

| Вид | Расположение | Назначение |
|-----|--------------|------------|
| Unit-тест парсера | `tests/parser/test_footnote_parser.py` | Markdown → AST |
| Unit-тест handler | `tests/elements/test_footnote.py` | AST → фрагменты OOXML |
| Golden-тест | `tests/expected/footnote.document.xml` | Полный снимок `document.xml` |
| Интеграционный тест | `tests/integration/test_footnote_docx.py` | Сквозной DOCX |

После намеренных изменений OOXML перегенерируйте golden-файлы:

```bash
python scripts/update-golden.py
# or: pytest tests/golden/ --update-golden
```

### Чеклист

- [ ] Dataclass AST + обновление union
- [ ] Парсер эмитит новый тип узла
- [ ] Handler в `elements/<name>.py`
- [ ] OOXML builder + фасад `api.py`
- [ ] `registry.register("<type>", …)` в `create_default_registry()`
- [ ] Тесты (parser, handler, golden, integration)
- [ ] **Не** меняйте `AstProcessor`, пока не меняется сам алгоритм обхода дерева

## Плагины

Загружайте доверенные Python-расширения через `--plugin`:

```bash
md2docx README.md --plugin examples/plugins/notes_plugin.py -o README.docx
```

См. [`docs/PLUGINS.md`](docs/PLUGINS.md) и [`docs/PLUGIN_API.md`](docs/PLUGIN_API.md).

Предпочтительный поток рендеринга плагина:

```text
Directive → Custom AST → Handler → RichDocumentFragment → existing pipeline → DOCX
```

Для новых плагинов используйте `md2docx.semantic`. См. [`docs/API.md`](docs/API.md#rich-semantic-api).

## Стабильность API

Публичная поверхность разделена по tier и покрыта тестами в `tests/contracts/`:

| Tier | Поверхность | Стабильность |
|------|-------------|--------------|
| A | `md2docx.plugin_api` (только `__all__`) | Stable v1 |
| B | `styles.definition`, `ooxml.api` (legacy), `semantic` | Стабильные дополнения для плагинов |
| C | CLI-флаги, коды выхода, семантика `--plugin` | Поведенческий контракт |
| D | `convert_markdown_to_docx`, themes, templates, validation | Экспериментальный programmatic API |

Манифест и политика совместимости: [`docs/API.md`](docs/API.md). Авторам плагинов — [`docs/PLUGIN_MIGRATION.md`](docs/PLUGIN_MIGRATION.md). Добавление или удаление символов Tier A требует обновления `tests/contracts/api_manifest.json`.

## Registry handlers

Нет центрального `switch` — handlers регистрируются по строке типа узла AST:

```python
registry = HandlerRegistry()
registry.register("paragraph", ParagraphHandler())
registry.register("heading", HeadingHandler())
registry.register("strong", StrongHandler())
processor = AstProcessor(registry)
```

Встроенная проводка живёт в `elements.create_default_registry()` (composition root).

## ProcessingContext

Каждый handler получает один и тот же общий контекст. Handlers **не должны** создавать собственные `RelationshipManager`, `NumberingManager` и т.п.

```python
@dataclass
class ProcessingContext:
    document: OoxmlDocument              # накопление элементов body
    relationships: RelationshipManager   # централизованные rId / .rels
    styles: StyleManager                 # семантическая роль → Word style id
    numbering: NumberingManager          # выделение numId для списков
    media: MediaManager                  # части word/media/*
    # transient: list_level, run_collector, block_style, …
```

Создаётся один раз на конвертацию через `ProcessingContext.create_default(source_dir=…)`.

## OOXML API

Handlers вызывают высокоуровневый фасад вместо сборки сырого XML:

```python
from md2docx.ooxml import api

context.run_collector.append(api.run(api.text("Hello")))
context.run_collector.append(api.run("bold", bold=True))
context.document.add_heading(runs, style_id="Heading1")
context.document.add_table(table_ast, rows)
```

Низкоуровневые модули (`ooxml/paragraph.py`, `run.py`, `text.py`, …) внутренние для слоя OOXML.

## Части пакета DOCX

`DocxPackageWriter` управляет каждой частью вывода:

| Часть | Builder |
|-------|---------|
| `word/document.xml` | `OoxmlDocument` + обёртка body |
| `word/styles.xml` | `ooxml/styles.py` |
| `word/numbering.xml` | `NumberingManager` (когда есть списки) |
| `word/_rels/document.xml.rels` | `RelationshipManager` |
| `word/media/*` | `MediaManager` |
| `docProps/core.xml` | `core_props.py` (с YAML-метаданными) |
| `[Content_Types].xml` | `content_types.py` |
| `_rels/.rels` | `RelationshipManager` |

## Валидация DOCX

Автоматический валидатор пакета (`md2docx.validation`) проверяет структурную корректность без открытия LibreOffice или Word:

```text
Markdown → DOCX → unzip → validate package → validate XML → validate relationships → validate references
```

| Проверка | Категория | Что проверяет |
|----------|-----------|---------------|
| Целостность ZIP | `package` | архив не повреждён, обязательные части на месте |
| Well-formed XML | `xml` | каждая часть `.xml` / `.rels` парсится |
| UTF-8 | `unicode` | части декодируются как UTF-8 |
| Content Types | `content_types` | каждая запись ZIP покрыта `[Content_Types].xml` |
| Relationships | `relationships` | цели `_rels/.rels` и `document.xml.rels` резолвятся |
| References | `references` | нет висячих `r:id` / `r:embed` в `document.xml` |
| Styles | `styles` | `w:pStyle` / `w:rStyle` ссылаются на определённые стили |
| Numbering | `numbering` | значения `w:numId` есть в `numbering.xml` |
| Media | `media` | у изображений есть rels, magic bytes совпадают с расширением |

```bash
python scripts/validate-docx.py out/bold.docx          # валидация одного файла
python scripts/validate-docx.py --fixtures             # конвертация + валидация всех fixtures
md2docx tests/fixtures/bold.md -o /tmp/bold.docx --validate
pytest tests/validation/ -q                            # те же проверки в CI
```

Структурная валидация ловит битый XML, висячие rId и отсутствующие части — типичные причины диалогов восстановления в Word/LibreOffice. Ручной smoke-тест в Word/LibreOffice перед релизом всё равно рекомендуется.

## Тестирование

```bash
pytest -q                                    # полный набор (~238 тестов)
pytest tests/parser/test_ast_fixtures.py -q  # снимки Markdown → AST
pytest tests/golden/ -q                      # golden-файлы document.xml
pytest tests/validation/ -q                  # валидация пакета DOCX
pytest tests/architecture/ -q                # охрана границ слоёв
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py                  # пишет out/BENCHMARK.md
```

Матрица тестов: [`docs/TEST_MATRIX.md`](docs/TEST_MATRIX.md).

AST-fixtures парсера живут в `tests/fixtures/ast/*.md` + `*.ast.json` (без DOCX).

Опциональный гейт LibreOffice: `pytest tests/integration/test_libreoffice_compat.py` (пропускается, если не установлен).

## Поддерживаемый Markdown

| Конструкция | Поддержка |
|-------------|-----------|
| Абзацы | да |
| Заголовки `#`–`###` | да |
| **Жирный**, *курсив*, вложенные | да |
| `` `inline code` `` | да |
| `[links](url)` | да (внешние + внутренние `#anchor`) |
| `<https://...>` autolinks | да |
| `[text][ref]` reference links | да |
| `~~strikethrough~~` | да |
| `- [ ]` / `- [x]` task lists | да (префикс-глиф) |
| Жёсткий перенос (`  ` / `\`) | да |
| `<!-- toc -->` / `<!-- toc: 1-3 -->` | да |
| `-` / `1.` списки, вложенные | да |
| `>` цитата | да |
| `---` горизонтальная линия | да |
| Fenced code blocks | да |
| `![alt](path)` изображения (PNG, JPEG, …) | да |
| GFM-таблицы + cell directives | да |
| YAML front matter | да |

Изображения должны существовать под каталогом Markdown-файла (только относительные пути; `../` за пределы дерева источника отклоняется). Отсутствующие изображения дают `Error: image not found: ...`.

## Известные ограничения

Не поддерживается в этом релизе:

- Сноски, definition lists
- Сырые HTML-блоки и inline HTML
- Bare URL autolink (без `<>`)
- Math (LaTeX), диаграммы (Mermaid)
- Комментарии
- Разные колонтитулы первой/нечётной/чётной страницы
- Пользовательские шаблоны / темы Word

Внутренне есть встроенная система тем (`DefaultTheme`, token-based `ThemeResolver`). Внешние файлы тем и CLI `--theme` пока не выставлены. См. [`docs/THEMES.md`](docs/THEMES.md).

Неподдерживаемые типы узлов AST завершаются с `Error: unsupported AST node: <type>`.

## Чеклист ручной проверки в Word

После генерации DOCX (особенно `integration-article.docx`) откройте в Microsoft Word:

- [ ] DOCX открывается без диалога восстановления
- [ ] Заголовки отображаются с правильными уровнями и стилями
- [ ] Нумерованные и маркированные списки корректны (включая вложенные)
- [ ] Гиперссылки кликабельны
- [ ] Изображения отображаются разумного размера
- [ ] Таблицы: заголовки, границы, выравнивание, объединения
- [ ] Unicode (кириллица, CJK, арабский, emoji) отображается корректно
- [ ] Жирный / курсив / inline-код сохранены в тексте и ячейках таблиц

## Разработка

```bash
pytest -q                              # unit, integration, golden, architecture, validation
python scripts/build-out.py            # тесты + сборка всех fixture DOCX → out/
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py
python scripts/update-golden.py        # обновить tests/expected/*.document.xml
md2docx tests/fixtures/bold.md -o /tmp/bold.docx --validate
```

`scripts/build-out.py` пишет в `out/`:

- `test-results.txt` — вывод pytest
- `<name>.docx` — сгенерированные архивы
- `<name>/` — распакованный DOCX с pretty-printed XML
- `BUILD_RESULTS.md` — сводка

Отдельной lint-команды пока нет; после каждого изменения запускайте `pytest -q`.

## Правила разработки

1. **Итерируйте** — не реализуйте все фичи сразу; поставляйте маленькими итерациями.
2. **Планируйте каждую итерацию** — до кода сформулируйте Goal, Files, Tests, Expected result.
3. **Проверяйте** — после каждой итерации запускайте тесты (и lint/build, когда есть).
4. **Не регрессируйте** — существующие fixtures и golden-тесты должны продолжать проходить.
5. **Держите просто** — без абстракций, пока не появится второй сценарий использования.
6. **Соблюдайте границы слоёв** — Markdown, AST, Processing, OOXML, ZIP остаются раздельными.
7. **Один handler на элемент** — каждая конструкция Markdown → один класс handler.
8. **Один processor** — один `AstProcessor` владеет обходом AST.
9. **OOXML в своём слое** — handlers идут через `ooxml.api`, не через сырые XML-строки.
10. **Упаковка DOCX ниже OOXML** — сборка ZIP только в `ooxml/package.py`.

Тесты границ архитектуры в `tests/architecture/test_layer_boundaries.py` автоматически проверяют часть этих правил.

## Технологии

Реализация на **Python** (спецификация проекта допускает любой язык; для автономного прототипа выбран Python):

| Задача | Выбор |
|--------|-------|
| Язык | Python 3.9+ |
| Парсер Markdown | [markdown-it-py](https://github.com/executablebooks/markdown-it-py) (токен-поток → AST) |
| XML | [lxml](https://lxml.de/) через `ooxml/xml_builder.py` (без XML из строковых шаблонов) |
| ZIP / DOCX | stdlib `zipfile` |
| Тесты | pytest (unit, integration, golden, architecture) |
| CLI | argparse |

Мы сознательно **не** используем библиотеку, скрывающую генерацию OOXML/DOCX (python-docx, pandoc и т.п.). Мы владеем:

- `document.xml`
- `styles.xml`
- `numbering.xml`
- relationships
- media
- `[Content_Types].xml`

При портировании на TypeScript действует то же разделение слоёв: markdown-it или аналог → AST → registry handlers → XML builder (эквивалент lxml) → ZIP-библиотека → Vitest/Jest.

## История итераций

| Итер. | Фича |
|-------|------|
| 0 | Scaffold: CLI, AST, processor, OOXML, тесты |
| 1 | Пустой Markdown → валидный DOCX |
| 2 | Обычные текстовые абзацы |
| 3 | Несколько абзацев |
| 4 | Заголовки `#`–`###` |
| 5–6 | Жирный, курсив |
| 7 | Вложенное inline-форматирование |
| 8 | Inline-код |
| 9 | Ссылки + hyperlinks rels |
| 10–12 | Маркированные, нумерованные, вложенные списки + numbering.xml |
| 13 | Цитата |
| 14 | Горизонтальная линия |
| 15 | Fenced code blocks |
| 16 | Экранирование XML (безопасная сериализация) |
| 17 | Изображения + word/media |
| 18–20 | Таблицы, форматирование, объединения, cell directives |
| 21 | Вложенный inline + edge cases экранирования |
| 22 | YAML front matter → docProps |
| 23 | Стили Word (заголовки, Quote, Code, NoSpacing) |
| 24 | Рефакторинг границ слоёв, StyleManager/MediaManager |
| 25 | HandlerRegistry + фасад OOXML API |
| 26 | Безопасный XML builder (lxml, без f-string XML) |
| 27 | Golden-тесты (`tests/expected/*.document.xml`) |
| 28 | CLI UX (`--help`, `--version`, понятные ошибки) |
| 29 | Валидатор пакета DOCX (XML, rels, content types, media) |
| 30 | Production Readiness Audit (238 тестов, `--validate`, AST fixtures, безопасность изображений) |
| 31 | Rendering Context & Inline Formatting Model (RenderContext, централизованное OOXML-форматирование) |
| 32 | Style System & Document Theme Foundation (StyleRegistry, DefaultTheme, StylesXmlWriter) |
| 33 | Lists, Numbering & Table Styles (ListParagraph, разделение numbering, TableGrid, tblHeader) |
| 34 | Sections, Page Layout, Headers & Footers (SectionManager, page/section breaks, части header/footer) |
| 35 | Bookmarks, Internal/External Hyperlinks, TOC fields (BookmarkManager, slug-якоря, поле TOC Word) |
| 36 | GFM-совместимость (task lists, strikethrough, autolinks, hard breaks) |
| 37 | Document Theme System (tokens, ThemeResolver, переключение тем) |
| 38 | Dynamic DOCX Fields (PAGE, REF, SEQ, директивы header/footer) |
| 39 | Figures, Captions, Sequences & Cross-References (CaptionService, SEQ Figure/Table, REF `\r \h`; внутренний API) |
| 40 | Advanced Document Navigation (NavigationRegistry, LOF/LOT, remapping закладок шаблона, typed REF validation) |

## Подписи и перекрёстные ссылки (Iteration 20)

- Подписи к рисункам: через внутренний AST API (`Figure` + `Caption`)
- Подписи к таблицам: через `TableWithCaption`
- Перекрёстные ссылки на рисунки/таблицы: `CrossReference` с REF `\r \h`
- Автонумерация: поля Word `SEQ Figure` / `SEQ Table` (не счётчики Python)
- Markdown-синтаксис подписей: **отложен** — см. [`docs/FIGURES_AND_REFERENCES.md`](docs/FIGURES_AND_REFERENCES.md)

## Навигация по документу (Iteration 21)

- `NavigationRegistry` — семантические цели heading/figure/table в порядке документа
- Список рисунков / список таблиц — поля Word `TOC \c` (программный AST)
- Remapping имён закладок шаблона — суффикс коллизии `-1`; перепись REF/якорей в сгенерированном фрагменте
- Typed-валидация перекрёстных ссылок через `ReferenceManager`
- См. [`docs/NAVIGATION.md`](docs/NAVIGATION.md)

## Структура проекта

```text
ast-processor/
├── src/md2docx/
│   ├── cli/           # команда md2docx
│   ├── parser/        # Markdown → AST
│   ├── ast/           # типы узлов
│   ├── processor/     # AstProcessor, registry, context
│   ├── elements/      # handlers (один файл на элемент)
│   ├── ooxml/         # XML builders, API, writer DOCX
│   └── pipeline.py    # связывает слои
├── tests/
│   ├── fixtures/      # примеры .md
│   ├── expected/      # golden-снимки document.xml
│   ├── golden/        # тесты структурного сравнения XML
│   ├── integration/   # сквозные тесты DOCX
│   └── architecture/  # охрана границ слоёв
└── scripts/
    ├── build-out.py
    └── update-golden.py
```
