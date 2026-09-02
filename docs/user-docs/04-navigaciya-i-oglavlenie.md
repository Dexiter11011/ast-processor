# 04 — Навигация и оглавление

Раздел описывает HTML-комментарии-директивы для оглавления, списков рисунков и таблиц, подписей и перекрёстных ссылок.

## Оглавление и списки

```markdown
<!-- toc -->
<!-- toc: 1-3 -->
<!-- lof -->
<!-- lot -->
```

| Директива | Назначение |
|-----------|------------|
| `<!-- toc -->` | Оглавление по заголовкам (уровни 1–3) |
| `<!-- toc: 1-3 -->` | Оглавление с явным диапазоном уровней |
| `<!-- toc: 2-3 -->` | Только заголовки 2–3 уровня |
| `<!-- lof -->` | Список рисунков (List of Figures) |
| `<!-- lot -->` | Список таблиц (List of Tables) |

Разместите директивы в начале документа (после front matter и колонтитулов), перед основным текстом.

После открытия DOCX в Word нажмите **Ctrl+A → F9**, чтобы обновить поля — оглавление и списки заполнятся автоматически.

## Подписи к рисункам

Директива caption ставится **сразу после** изображения:

```markdown
![Схема](schema.png)

<!-- caption: figure Обзор архитектуры -->
```

Результат в Word: нумерованный рисунок «Рисунок N — Обзор архитектуры», закладка для перекрёстных ссылок.

## Подписи к таблицам

Директива caption ставится **сразу перед** таблицей:

```markdown
<!-- caption: table Конфигурационные параметры -->

| Параметр | Значение |
|----------|----------|
| Timeout  | 30       |
```

Результат: «Таблица N — Конфигурационные параметры».

## Перекрёстные ссылки (block directive)

Ссылка на рисунок или таблицу — отдельная строка-директива:

```markdown
<!-- ref: figure obzor-arhitektury -->
<!-- ref: figure obzor-arhitektury prefix="См. " -->
<!-- ref: table konfiguracionnye-parametry prefix="Описано в " -->
```

| Атрибут | Значение |
|---------|----------|
| `figure` / `table` | Тип объекта (рисунок или таблица) |
| slug | Идентификатор закладки (см. ниже) |
| `prefix="..."` | Текст перед номером (по умолчанию: `"See "` / можно задать `"См. "`) |

### Правила slug

Подпись «Обзор архитектуры» → закладка `figure-obzor-arhitektury`.

| В slug | Результат |
|--------|-----------|
| `architecture-overview` | `figure-architecture-overview` |
| `figure-architecture-overview` | используется как есть |
| `Architecture overview` | преобразуется в `figure-architecture-overview` |

Slug в `<!-- ref: ... -->` должен соответствовать slug подписи из `<!-- caption: ... -->`.

## Ссылки на заголовки (отличие от caption ref)

Для ссылок **на заголовки** используйте другие механизмы:

```markdown
[См. раздел «Архитектура»](#arhitektura)

<!-- field: ref arhitektura -->
```

Эти ссылки ведут на bookmark заголовка, а не на подпись рисунка/таблицы.

| Механизм | Цель | Пример |
|----------|------|--------|
| `[текст](#slug)` | Заголовок | inline-ссылка |
| `<!-- field: ref slug -->` | Заголовок | поле REF в абзаце |
| `<!-- ref: figure slug -->` | Рисунок | block directive |
| `<!-- ref: table slug -->` | Таблица | block directive |

## Полный пример

```markdown
<!-- toc: 1-2 -->
<!-- lof -->
<!-- lot -->

# Введение

![Обзор архитектуры](logo.png)

<!-- caption: figure Обзор архитектуры -->

<!-- ref: figure obzor-arhitektury prefix="См. " -->

<!-- caption: table Конфигурационные параметры -->

| Имя | Значение |
|-----|----------|
| A   | 1        |

<!-- ref: table konfiguracionnye-parametry prefix="См. " -->
```

Рабочий fixture: [`navigation-dsl.md`](../../tests/fixtures/markdown/navigation/navigation-dsl.md).

## Типичные ошибки

| Ошибка | Причина |
|--------|---------|
| `orphan caption directive` | Caption не рядом с image/table |
| `reference target ... not a figure target` | `ref: figure` на таблицу или неверный slug |
| Пустой LOF/LOT | Нет caption-директив или поля не обновлены в Word |

Подробнее — в [08-ogranicheniya-i-faq.md](08-ogranicheniya-i-faq.md).

## Следующий раздел

[Поля и колонтитулы](05-polya-i-kolontituly.md) — metadata, dynamic fields, разрывы страниц.
