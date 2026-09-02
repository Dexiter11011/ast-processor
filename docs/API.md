# Справочник публичного API

md2docx разделяет **стабильные публичные контракты** и **внутреннюю реализацию**. Для внешнего использования поддерживаются только символы, перечисленные в этом документе (или в связанных поддокументах ниже).

## Уровни API

### Уровень A — Plugin API v1 (стабильный)

Пространство имён: `md2docx.plugin_api`

Все символы уровня A перечислены в `__all__` файла [`plugin_api/__init__.py`](../src/md2docx/plugin_api/__init__.py) и продублированы в [`tests/contracts/api_manifest.json`](../tests/contracts/api_manifest.json).

Изменения машиночитаемого манифеста требуют явного обновления манифеста и контрактных тестов.

Подробности использования см. в [`PLUGIN_API.md`](PLUGIN_API.md).

### Уровень B — Дополнения для плагинов (стабильные вместе с plugin API v1)

Эти модули стабильны для авторов плагинов, но не реэкспортируются из `plugin_api`:

| Модуль | Символы |
|--------|---------|
| `md2docx.styles.definition` | `StyleDefinition`, `ParagraphStyle`, `RunStyle` |
| `md2docx.ooxml.api` | Устаревшие OOXML-билдеры (`paragraph`, `run`, `text`, …) |
| `md2docx.semantic` | Rich Semantic API (`RichDocumentFragment`, `paragraph`, `text`, `bold`, …) |

Обработчики могут возвращать `RichDocumentFragment` из `process()` или рендереров регионов шаблона. Для новых плагинов предпочтителен `md2docx.semantic`.

Обработчики получают объекты времени выполнения от движка (`context`, `processor`). Оборачивайте их в `SemanticContext.from_processing_context(context)` при вызове `render()`. **Не** импортируйте `md2docx.processor.*` в плагинах.

## Rich Semantic API

Пространство имён: `md2docx.semantic` (уровень B)

Создавайте содержимое документа как неизменяемые семантические значения, а не сырой OOXML:

```python
from md2docx.semantic import RichDocumentFragment, bold, fragment, paragraph, text

return fragment(
    paragraph("example.notes.note", bold(text("Note: ")), text("Important"))
)
```

Поддерживаемые операции:

- Абзацы со стилизованными встроенными фрагментами (`text`, `bold`, `italic`, `strike`, `inline_code`)
- `line_break()`, `hyperlink()`, `hyperlink_to()`
- Поля из белого списка (`page_field`, `title_field`, `ref_field`, …)
- `image()`, `figure()`, `cross_reference()`
- `bullet_list()`, `ordered_list()`
- Абзацы с `bookmark()`
- Композиция фрагментов через `+` и `fragment(...)`

Не поддерживается в v1: произвольный OOXML, произвольные инструкции полей, сырые `numId`/`rId`, URL удалённых изображений, семантические таблицы.

Обоснование проектных решений см. в [`ITERATION_28_AUDIT.md`](ITERATION_28_AUDIT.md).

### Уровень C — Поведенческий контракт CLI (стабильный)

| Аспект | Контракт |
|--------|----------|
| Точка входа | `md2docx INPUT [-o OUTPUT]` |
| `--plugin PATH` | Повторяемый; загружает Python-плагины в порядке аргументов |
| Коды выхода | `0` — успех, `1` — использование/конфигурация ввода, `2` — ошибки конвертации/валидации |
| Ошибки | `Error: {message}` в stderr без traceback в обычном режиме |
| `--debug` | Полный traceback только для неожиданных внутренних ошибок |
| `--validate` | Валидирует временный вывод перед атомарной заменой; при сбое сохраняет существующий файл |
| Ввод/вывод | Отклоняет каталоги на входе, каталоги на выходе и идентичные пути ввода/вывода |

См. [`ERROR_HANDLING.md`](ERROR_HANDLING.md) и [`PLUGINS.md`](PLUGINS.md).

### Уровень D — Программная интеграция (экспериментальный)

Эти подпакеты экспортируют символы через `__all__`, но пока не версионируются так же строго, как уровень A:

- `md2docx.pipeline.convert_markdown_to_docx`
- `md2docx.metadata`
- `md2docx.themes`
- `md2docx.templates`
- `md2docx.validation`

Используйте для интеграционного тестирования и инструментов; ожидайте менее строгих гарантий стабильности, чем у уровня A.

## Внутреннее (не поддерживается)

Недокументированные импорты могут измениться без предупреждения:

```text
md2docx.parser.*
md2docx.processor.*
md2docx.elements.*
md2docx.templates.merger
md2docx.ooxml.* (except api facade)
md2docx.ast.*
md2docx.plugins.loader
```

## Политика совместимости

| Тип изменения | Политика |
|---------------|----------|
| Аддитивный символ уровня A | Обновить манифест + документацию + контрактные тесты |
| Критическое изменение уровня A | Увеличить `PLUGIN_API_VERSION` |
| Внутренний рефакторинг | Допустим, если контрактные тесты проходят |
| Структура OOXML/XML | Может измениться, если семантическое поведение сохранено |

## Контракт ошибок

Публичные ошибки плагинов предоставляют стабильные атрибуты `code` (см. [`plugin_api/errors.py`](../src/md2docx/plugin_api/errors.py)). Контрактные тесты проверяют **типы** и **коды** исключений, а не полные строки сообщений.

| Исключение | Код |
|------------|-----|
| `PluginLoadError` | `plugin_load_error` |
| `DuplicateRegistrationError` | `duplicate_registration` |
| `RegistryFrozenError` | `registry_frozen` |
| `UnsupportedApiVersionError` | `unsupported_api_version` |
| `InvalidPluginNameError` | `invalid_plugin_name` |
| `ReservedNameError` | `reserved_name` |

Сбои валидации имён (`InvalidPluginNameError`, `ReservedNameError`) в совокупности покрывают ошибки валидации, описанные в проектной документации как `PluginValidationError`.

## Контрактные тесты

Запуск:

```bash
pytest tests/contracts/ -q
```

Снимочный тест манифеста завершится с ошибкой, если `plugin_api.__all__` изменится без обновления `api_manifest.json`.

## Связанная документация

- [`PLUGIN_API.md`](PLUGIN_API.md) — справочник расширений для плагинов
- [`PLUGIN_MIGRATION.md`](PLUGIN_MIGRATION.md) — заметки по миграции на API v1
- [`ERROR_HANDLING.md`](ERROR_HANDLING.md) — коды выхода, атомарный вывод, `--debug`
- [`RELEASE_READINESS.md`](RELEASE_READINESS.md) — чеклист релиза
