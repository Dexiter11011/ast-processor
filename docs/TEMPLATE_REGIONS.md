# Регионы навигации в шаблоне

Итерация 25 добавляет типизированные регионы шаблона для блоков навигации наряду с существующей точкой вставки `{{content}}`.

## Плейсхолдеры регионов

Поддерживаемые плейсхолдеры в отдельном абзаце:

```text
{{content}}
{{toc}}
{{list_of_figures}}
{{list_of_tables}}
{{title}}
{{author}}
{{date}}
{{subject}}
{{keywords}}
```

Регионы навигации рендерят абзацы полей Word, используя тот же стек, что и директивы Markdown (`TocManager`, существующие обработчики). Второй движок рендеринга не вводится.

## Правила

| Регион | Уникальность | Поведение |
|--------|------------|----------|
| `{{content}}` | Ровно один (обязательно) | Полный фрагмент тела Markdown |
| `{{toc}}` | Дубликаты допустимы | Поле TOC (уровни 1–3) |
| `{{list_of_figures}}` | Дубликаты допустимы | Поле LOF |
| `{{list_of_tables}}` | Дубликаты допустимы | Поле LOT |
| Scalars | Дубликаты допустимы | Замена текста на месте |

Дополнительные ограничения:

- Плейсхолдер должен быть единственным текстом в своём абзаце (разделённые runs допустимы)
- Встроенные плейсхолдеры (`Project: {{title}}`) → ошибка
- Неизвестные плейсхолдеры → ошибка
- Регионы в колонтитулах **не поддерживаются** в v1 (сканируются только абзацы непосредственно в `w:body`)
- Без выражений, фильтров и скриптов

## Порядок в шаблоне

Регионы составляются в **порядке документа шаблона**. Шаблон может разместить навигацию до или после контента:

```text
Title:
{{title}}

{{content}}

Appendix navigation
{{toc}}
{{list_of_figures}}
```

Word разрешает поля TOC/LOF/LOT при открытии/обновлении относительно полного объединённого документа, поэтому регионы навигации могут располагаться в шаблоне до сгенерированного контента.

## Политика дедупликации: шаблон побеждает

Когда шаблон содержит регион навигации, соответствующие директивы Markdown удаляются из AST **до** рендеринга контента:

| Регион шаблона | Удаляемая директива Markdown |
|-----------------|----------------------------|
| `{{toc}}` | `<!-- toc -->` / `TableOfContents` |
| `{{list_of_figures}}` | `<!-- lof -->` / `ListOfFigures` |
| `{{list_of_tables}}` | `<!-- lot -->` / `ListOfTables` |

Это предотвращает дублирование блоков навигации, когда и шаблон, и Markdown задают один и тот же регион.

## Архитектура

```text
Template DOCX
    ↓ scan regions
Markdown AST
    ↓ strip navigation nodes for template regions
AstProcessor → content fragment (body_children)
    +
TocManager → navigation fragments (on demand)
    ↓
TemplateMerger (single remapping pass on content fragment)
    ↓
TemplateComposer (multi-region compose, back-to-front insertion)
    ↓
Final DOCX
```

Ключевые компоненты:

| Модуль | Роль |
|--------|------|
| `templates/regions.py` | Перечисление `TemplateRegionKind` |
| `templates/placeholders.py` | Реестр `PlaceholderKind.NAVIGATION` |
| `templates/composition_plan.py` | `TemplateCompositionPlan` |
| `templates/composition.py` | Рендеринг фрагментов навигации |
| `templates/composer.py` | Составление нескольких регионов |
| `parser/navigation_transform.py` | Дедупликация AST |

## Обратная совместимость

Существующие шаблоны только с `{{content}}` и скалярными плейсхолдерами ведут себя точно так же, как в итерациях 17/18. Форма `{{ content }}` (с внутренними пробелами) теперь принимается согласованно при сканировании и вставке.

## Сборка фикстур регионов

```bash
PYTHONPATH=src python scripts/build-template-fixtures.py
```

Создаёт:

- `tests/fixtures/templates/regions-basic.docx` — `{{toc}}` + `{{content}}`
- `tests/fixtures/templates/regions-navigation.docx` — TOC + LOF + LOT + `{{content}}`
- `tests/fixtures/templates/regions-complex.docx` — скаляры, контент перед навигацией

См. также [`DOCX_TEMPLATES.md`](DOCX_TEMPLATES.md) и [`NAVIGATION.md`](NAVIGATION.md).
