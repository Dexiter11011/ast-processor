# Справочник Plugin API

Публичное пространство имён: `md2docx.plugin_api`

Внутренние модули (билдеры `md2docx.ooxml.*`, `md2docx.templates.merger`, полная мутация `ProcessingContext`) не входят в стабильный контракт плагинов.

## Версия API

```python
from md2docx.plugin_api import PLUGIN_API_VERSION  # "1"
```

Плагины объявляют `PluginMetadata.api_version = "1"`. Неподдерживаемые версии вызывают `UnsupportedApiVersionError`.

## Интерфейс плагина

```python
from md2docx.plugin_api import PluginMetadata, PluginRegistry

class MyPlugin:
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="acme.demo", version="1.0.0")

    def register(self, registry: PluginRegistry) -> None:
        ...

plugin = MyPlugin()
```

Точка входа для `--plugin PATH`: объект `plugin` на уровне модуля (или вызываемый `get_plugin()`).

## PluginRegistry

Фасад над разрешёнными типами расширений. Делегирует существующим реестрам ядра, где это возможно.

| Метод | Назначение |
|-------|------------|
| `register_handler(type, handler)` | Тип узла AST → `ElementHandler` |
| `register_style(StyleDefinition)` | Семантический стиль через `StyleRegistry` |
| `register_directive(DirectiveDefinition)` | HTML-комментарий-директива → AST |
| `register_template_region(TemplateRegionDefinition)` | Плейсхолдер шаблона → фрагмент |
| `register_validator(ValidatorDefinition)` | Валидация по фазам |
| `freeze()` | Блокировка реестра перед конвертацией |

После `freeze()` все вызовы `register_*` вызывают `RegistryFrozenError`.

Дублирующие регистрации вызывают `DuplicateRegistrationError`.

## Политика пространств имён

| Ресурс | Пример |
|--------|--------|
| Имя плагина | `example.notes` |
| Тип AST | `example.notes.note` |
| Семантический id стиля | `example.notes.note` |
| Регион шаблона | `example_note` |
| Имя валидатора / директивы | `example.notes.validate_notes` |

Имена ядра (`paragraph`, `content`, `toc`, …) зарезервированы.

## Обработчики

Реализуйте существующий протокол обработчика:

```python
def process(self, node, context, processor) -> None:
    ...
```

Используйте билдеры `md2docx.ooxml.api` и `context.document.add_body_element()`. Не редактируйте сырой XML или части ZIP.

## Директивы

```python
DirectiveDefinition(
    name="example.notes.directive",
    pattern=re.compile(r'^\s*<!--\s*note:\s*(?P<text>.+?)\s*-->\s*$', re.I),
    to_ast=lambda match, line_no: CustomNote(text=match.group("text")),
)
```

Директивы сопоставляются на отдельных строках после встроенных директив.

## Регионы шаблона

```python
TemplateRegionDefinition(
    placeholder_name="example_note",
    render_fragment=lambda context: [...],
    strip_ast_types=frozenset({"example.notes.note"}),
)
```

Шаблон имеет приоритет над Markdown: при наличии `{{example_note}}` соответствующие узлы AST удаляются из фрагмента содержимого перед рендерингом.

## Валидаторы

```python
from md2docx.plugin_api import ValidationPhase, ValidatorDefinition

ValidatorDefinition(
    name="example.notes.validate",
    phase=ValidationPhase.SEMANTIC,
    validate=lambda document: ...,
)
```

Фазы:

| Фаза | Когда |
|------|-------|
| `PARSE` | После Markdown → AST |
| `SEMANTIC` | После обхода `process_document`, до валидации навигации |
| `RENDER` | После рендеринга, до записи пакета |
| `PACKAGE` | Зарезервировано для будущих post-package хуков |

## CLI

```bash
md2docx input.md --plugin ./my_plugin.py -o output.docx
```

Сбои загрузки выводят `Error: ...` без traceback в обычном режиме.

## Матрица совместимости

Поддерживается:

- Пользовательские узлы AST (namespaced dataclasses)
- Обработчики
- Директивы
- Семантические стили
- Регионы шаблона
- Валидаторы (PARSE / SEMANTIC / RENDER)

Не поддерживается:

- Произвольный сырой OOXML
- Доступ к ZIP
- Удалённая загрузка плагинов
- Резолвер зависимостей
- Регистрация целей навигации (v1)
- Песочница для плагинов

## См. также

- [`PLUGINS.md`](PLUGINS.md)
- [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md)
