---
title: Project Documentation
author: Ivan Petrov
date: 2026-08-31
subject: Example document
keywords: markdown, docx, metadata
---

# Introduction

This example demonstrates YAML front matter metadata for title, author, date, subject, and keywords.

CLI flags override front matter per field:

```bash
md2docx metadata.md \
  --title "Final Documentation" \
  --author "John Doe" \
  -o output.docx
```

Static `{{date}}` placeholders use metadata date. The Word `DATE` field is dynamic and independent — see [DOCUMENT_METADATA.md](../../docs/DOCUMENT_METADATA.md).
