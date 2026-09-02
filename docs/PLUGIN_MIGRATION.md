# Руководство по миграции Plugin API

Этот документ описывает, как создавать и поддерживать плагины для **Plugin API v1** (`PLUGIN_API_VERSION = "1"`).

## Поддерживаемые импорты

### Уровень A — `md2docx.plugin_api`

Импортируйте только символы, экспортируемые в `md2docx.plugin_api.__all__`:

- `Plugin`, `PluginMetadata`, `PluginRegistry`, `PLUGIN_API_VERSION`
- `DirectiveDefinition`, `TemplateRegionDefinition`, `ValidatorDefinition`, `ValidationPhase`
- `PluginError`, `PluginLoadError`, `DuplicateRegistrationError`, `RegistryFrozenError`, `UnsupportedApiVersionError`, `InvalidPluginNameError`, `ReservedNameError`

Полный манифест см. в [`API.md`](API.md).

### Уровень B — дополнения для плагинов

Эти модули стабильны для плагинов, но не реэкспортируются из `plugin_api`:

- `md2docx.styles.definition` — `StyleDefinition`, `ParagraphStyle`, `RunStyle`
- `md2docx.semantic` — Rich Semantic API (предпочтителен для рендеринга)
- `md2docx.ooxml.api` — устаревшие OOXML-билдеры (по-прежнему поддерживаются)

### Не импортируйте

Следующее **внутреннее** и может измениться без предупреждения:

- `md2docx.processor.*` (включая `ProcessingContext`, `AstProcessor`)
- `md2docx.parser.*`
- `md2docx.templates.merger`, `md2docx.templates.composer`
- `md2docx.ooxml.paragraph`, `md2docx.ooxml.run`, `lxml`

Методы обработчиков получают `context` и `processor` во время выполнения. Типизируйте их как `Any`. Предпочитайте возвращать `RichDocumentFragment` из обработчиков вместо ручной сборки OOXML.

## Миграция на Rich Semantic API

**До (устаревший путь OOXML):**

```python
from md2docx.ooxml import api

style_id = context.styles.to_ooxml(STYLE_ID)
paragraph = api.paragraph([api.run(f"Note: {node.text}")], style_id=style_id)
context.document.add_body_element(paragraph)
```

**После (Rich Semantic API):**

```python
from md2docx.semantic import bold, fragment, paragraph, text

return fragment(
    paragraph(STYLE_ID, bold(text("Note: ")), text(node.text))
)
```

Регионы шаблона могут возвращать `RichDocumentFragment` вместо `list[Element]`.

## Точка входа

Экспортируйте объект `plugin` на уровне модуля или функцию `get_plugin()`, возвращающую объект, реализующий:

```python
class Plugin(Protocol):
    @property
    def metadata(self) -> PluginMetadata: ...
    def register(self, registry: PluginRegistry) -> None: ...
```

Загрузка:

```bash
md2docx input.md --plugin path/to/plugin.py -o output.docx
```

## Правила именования

- Имя плагина: идентификатор с точками, например `example.notes`
- Типы AST обработчиков, стили, директивы, валидаторы и регионы шаблона должны быть namespaced под именем плагина
- Зарезервированные имена ядра (например, `paragraph`, `heading`) нельзя регистрировать

## Жизненный цикл реестра

1. `PluginRegistry.empty()`
2. Загрузка плагинов в порядке CLI; каждый вызывает `register()`
3. Реестр замораживается перед разбором
4. Дублирующие регистрации вызывают `DuplicateRegistrationError`
5. Регистрация после freeze вызывает `RegistryFrozenError`

## Обработка ошибок

Публичные ошибки плагинов предоставляют стабильный атрибут `code`. Контрактные тесты проверяют **тип** и **code**, а не полные строки сообщений.

| Исключение | `code` |
|------------|--------|
| `PluginLoadError` | `plugin_load_error` |
| `DuplicateRegistrationError` | `duplicate_registration` |
| `RegistryFrozenError` | `registry_frozen` |
| `UnsupportedApiVersionError` | `unsupported_api_version` |
| `InvalidPluginNameError` | `invalid_plugin_name` |
| `ReservedNameError` | `reserved_name` |

## Фазы валидации

| Фаза | Когда выполняется |
|------|-------------------|
| `PARSE` | После Markdown → AST |
| `SEMANTIC` | Во время обработки AST |
| `RENDER` | После построения OOXML-тела |
| `PACKAGE` | Зарезервировано; не подключено в pipeline v1 |

## Канонические примеры

- Полный пример: [`examples/plugins/notes_plugin.py`](../examples/plugins/notes_plugin.py)
- Rich-композиция: [`examples/plugins/rich_content_plugin.py`](../examples/plugins/rich_content_plugin.py)
- Контрактная фикстура (устаревший OOXML): [`tests/contracts/plugins/basic_plugin.py`](../tests/contracts/plugins/basic_plugin.py)

## Обновление до API v2

Когда `PLUGIN_API_VERSION` увеличивается:

1. Установите `api_version` в вашем `PluginMetadata` в соответствии с новой версией
2. Прочитайте release notes о переименованных или удалённых методах регистрации
3. Запустите контрактные тесты: `pytest tests/contracts/`

Критические изменения символов уровней A или B требуют новой версии API. Аддитивные изменения (новые опциональные хуки регистрации) могут остаться в рамках v1.

## Безопасность

Плагины загружаются только через `--plugin`. Markdown-комментарии вроде `<!-- plugin: ... -->` **не** загружают код. Относитесь к путям `--plugin` как к доверенным — это эквивалентно запуску произвольного Python.
