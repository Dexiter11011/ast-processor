# md2docx

Конвертер **Markdown → DOCX** через явный конвейер AST → OOXML.

Собирает настоящий пакет Office Open XML (`document.xml`, `styles.xml`, `numbering.xml`, relationships, media) без делегирования генерации «чёрному ящику» вроде python-docx.

## Быстрый старт

```bash
cd ast-processor
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

md2docx input.md -o output.docx
md2docx input.md -o output.docx --validate
md2docx --help
```

Требуется **Python 3.9+**.

## Документация

| Раздел | Описание |
|--------|----------|
| [Руководство пользователя](user-docs/README.md) | Установка, синтаксис, темы, pipeline |
| [Публичный API](API.md) | Стабильные контракты и уровни API |
| [Обработка ошибок](ERROR_HANDLING.md) | Коды выхода, `--debug`, атомарный вывод |
| [Плагины](PLUGINS.md) | Загрузка расширений и модель доверия |

## Возможности

- Абзацы, заголовки, жирный/курсив, код, ссылки, списки, таблицы
- YAML front matter и метаданные CLI
- Темы (`--theme`), шаблоны DOCX (`--template`)
- Оглавление, закладки, перекрёстные ссылки, поля Word
- Валидация пакета (`--validate`) и атомарная запись файла
- Plugin API и Rich Semantic API для расширений

## Репозиторий

Исходный код: [Dexiter11011/ast-processor](https://github.com/Dexiter11011/ast-processor).
