# Аудит готовности к production

Аудит pipeline Markdown → DOCX в md2docx. **Новые элементы Markdown не добавлялись.**

## До

| Метрика | Значение |
|---------|----------|
| Тесты | 200 passed |
| Обработчики | 16 зарегистрировано |
| Markdown-фикстуры | 24 |
| Валидатор DOCX | присутствует (10 категорий) |
| CLI `--validate` | отсутствует |
| Отсутствующее изображение | тихий пропуск |
| Безопасность путей | `../` разрешён |
| AST JSON-фикстуры | отсутствуют |
| Базовая линия производительности | отсутствует |

## Изменения

1. **`md2docx --validate`** — конвертация, затем запуск `validate_docx()`; код выхода 2 при сбое
2. **Ошибки изображений** — `ImageNotFoundError` / `ImagePathError`; fail fast; песочница путей под `source_dir`
3. **AST JSON-фикстуры** — `tests/fixtures/ast/*.md` + `*.ast.json` + снимочные тесты парсера
4. **Тесты обработчиков** — отдельные unit-тесты для `list_item`, `table_row`, `table_cell`
5. **Интеграционные аудит-тесты** — вложенное форматирование, списки, ссылки, изображения (PNG/JPEG/dual), таблицы, некорректный ввод, unicode
6. **Ворота LibreOffice** — опциональный headless-тест DOCX→PDF (пропуск, если не установлен)
7. **Architecture-тесты** — расширены import guards для слоя ooxml/validation
8. **Базовая линия производительности** — `scripts/benchmark.py` → `out/BENCHMARK.md`
9. **Документация** — README (Testing, Supported Markdown, Known limitations, Word checklist), `docs/TEST_MATRIX.md`

## Тесты

| | До | После |
|---|-----|-------|
| Всего | 200 | **238** |

## Валидация

| Проверка | Статус |
|----------|--------|
| ZIP | PASS (все фикстуры + `--validate`) |
| XML | PASS |
| Relationships | PASS |
| Content Types | PASS |
| Unicode | PASS (фикстура `unicode.md`) |
| Images | PASS (PNG, JPEG, dual; отсутствие → ошибка) |
| Lists | PASS (audit + ordered restart) |
| Tables | PASS |
| Nested formatting | PASS |

## LibreOffice

SKIPPED, если `libreoffice` / `soffice` не в PATH — см. `tests/integration/test_libreoffice_compat.py`.

## Производительность

| Размер | parse | process | package | total | peak MB |
|--------|-------|---------|---------|-------|---------|
| 10 KB | 0.009s | 0.001s | 0.002s | 0.012s | 0.4 |
| 100 KB | 0.078s | 0.005s | 0.002s | 0.084s | 0.6 |
| 1 MB | 0.584s | 0.030s | 0.008s | 0.623s | 6.8 |

Запуск: `python scripts/benchmark.py`

## Оставшиеся риски

1. Совместимость с Microsoft Word не автоматизирована — требуется ручной чеклист
2. Некорректный markdown (незакрытое выделение) принимает вывод парсера без строгого соответствия спецификации
3. Нет lint/typecheck в CI (ruff/mypy не настроены)
4. Golden-снимки не включают `integration-article` / `all-iterations` (большие файлы; валидируются структурно)

## Известные ограничения

См. README § Known limitations. Сноски, HTML, task lists и т. д. остаются вне области.

## Ворота качества

```bash
pytest -q                         # 238 passed
python scripts/validate-docx.py --fixtures
python scripts/benchmark.py
```

Lint/typecheck: не настроен (задокументированный пробел).
