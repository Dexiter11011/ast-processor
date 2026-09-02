# test/field — демо fields и metadata

## Файлы

| Файл | Назначение |
|------|------------|
| `fields-demo.md` | Исходник с front matter, таблицами полей и directives |
| `fields-demo.docx` | Сгенерированный DOCX |

## Пересборка

```bash
cd ast-processor
PYTHONPATH=src python -m md2docx.cli.main \
  test/field/fields-demo.md \
  -o test/field/fields-demo.docx \
  --validate
```

## Поля в демо

| Механизм | Поля |
|----------|------|
| YAML metadata | title, author, subject, keywords |
| Header directives | TITLE, AUTHOR, DATE |
| Footer directive | PAGE, NUMPAGES |
| Body directives | DATE, REF, SEQ |
| TOC | `<!-- toc -->` |
| Template placeholders | `{{title}}`, `{{author}}`, `{{date}}`, `{{content}}` (только с `--template`) |

## Что проверить в Word

- **Свойства файла** → title, author, subject, keywords из YAML
- **Header** → TITLE, AUTHOR, DATE (три строки)
- **Footer** → «Page N of M»
- **Body** → DATE, REF на «Ref Target Section», SEQ Figure, TOC
