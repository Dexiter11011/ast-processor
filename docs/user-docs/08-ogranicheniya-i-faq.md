# 08 — Ограничения и FAQ

## Что не поддерживается

| Функция | Альтернатива |
|---------|--------------|
| Raw HTML (`<div>`, `<table>`, `<br>`) | GFM Markdown, директивы md2docx |
| Footnotes (`[^1]`) | Сноски вручную или blockquote |
| Math (`$...$`) | Формулы как изображения |
| Bare URL (`https://...` без `<>`) | `<https://...>` или `[text](url)` |
| Inline cross-ref на рисунки | Block directive `<!-- ref: figure slug -->` |
| Mermaid / PlantUML | Экспорт диаграммы в PNG |
| Word interactive checkboxes | Task lists `- [ ]` (символы ☐/☑) |
| Header/footer directives + `--template` | Колонтитулы только из шаблона |

## Типичные ошибки

| Сообщение | Причина | Решение |
|-----------|---------|---------|
| `input file does not exist` | Неверный путь к `.md` | Проверьте путь и имя файла |
| `image not found: path.png` | Файл изображения не найден | Положите файл рядом с `.md` или исправьте путь |
| `orphan caption directive` | Caption не рядом с image/table | Figure: caption **после** image; table: caption **перед** table |
| `reference target ... not found` | Неверный slug в `<!-- ref: ... -->` | Проверьте slug подписи из `<!-- caption: ... -->` |
| `reference target ... not a figure target` | `ref: figure` на таблицу (или наоборот) | Исправьте kind: `figure` или `table` |
| `template insertion point not found` | В шаблоне нет `{{content}}` | Добавьте placeholder в DOCX-шаблон |
| `invalid theme: ...` | Ошибка в YAML-теме | Проверьте синтаксис и обязательные поля |
| `md2docx not found` (pipeline) | venv не установлен | Выполните установку из [раздела 01](01-ustanovka-i-zapusk.md) |
| `Lint failed for ...` (pipeline) | Markdown не парсится | Проверьте `docs/markdown/` на остатки HTML |

## FAQ

### Документ открывается с «Repair» в Word

Обычно означает некорректный OOXML. Запустите конвертацию с `--validate`:

```bash
md2docx document.md -o document.docx --validate
```

Если validation проходит, но Word всё равно предлагает repair — проверьте шаблон (`--template`) и сложные таблицы.

### Оглавление / LOF / LOT пустые

Word не обновил поля. Выделите весь документ (Ctrl+A) и нажмите F9 (Update Fields). Убедитесь, что конвертация выполнена с `--update-fields` или pipeline уже использует этот флаг.

### Номера рисунков не совпадают с refs

Обновите поля в Word (Ctrl+A → F9). Проверьте, что slug в `<!-- ref: figure ... -->` соответствует slug из `<!-- caption: figure ... -->`.

### Колонтитулы не появились

- Без `--template`: добавьте директивы `<!-- header: ... -->` / `<!-- footer: ... -->` в начало Markdown
- С `--template`: колонтитулы берутся из шаблона; Markdown-директивы игнорируются

### Pipeline не находит pandoc

Установите pandoc и убедитесь, что `pandoc` доступен в PATH:

```bash
pandoc --version
```

### Как добавить новый документ в pipeline?

1. Положите `.docx` в `docx/fresh-data/`
2. Запустите `python scripts/convert_pipeline.py`
3. Результат — в `docx/docs/output/`

## Чеклист проверки в Word

После получения DOCX проверьте:

- [ ] Документ открывается **без** диалога Document Recovery / Repair
- [ ] Оглавление заполнено (Ctrl+A → F9)
- [ ] Список рисунков / таблиц заполнен (если использовались `<!-- lof -->` / `<!-- lot -->`)
- [ ] Номера рисунков и таблиц корректны
- [ ] Перекрёстные ссылки (`<!-- ref: ... -->`) показывают правильные номера
- [ ] Колонтитулы: title, author, date, номера страниц
- [ ] Таблицы: границы, заливка, merge отображаются корректно
- [ ] Изображения на месте, не broken
- [ ] Шрифт PT Sans (при использовании корпоративной темы)
- [ ] Свойства документа (File → Info): title, author, subject, keywords

## Дополнительные ресурсы

| Документ | Аудитория |
|----------|-----------|
| [README.md](README.md) | Авторы — оглавление user-docs |
| [`ast-processor/docs/`](../ast-processor/docs/) | Разработчики — архитектура, API |
| [`MARKDOWN_CAPTION_DSL.md`](../ast-processor/docs/MARKDOWN_CAPTION_DSL.md) | Разработчики — DSL подробно |
| [`DYNAMIC_FIELDS.md`](../ast-processor/docs/DYNAMIC_FIELDS.md) | Разработчики — поля Word |
