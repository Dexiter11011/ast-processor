#!/usr/bin/env python3
"""Performance baseline for md2docx pipeline."""

from __future__ import annotations

import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"


def _synthetic_markdown(target_bytes: int) -> str:
    paragraph = "Lorem ipsum dolor sit amet. " * 20 + "\n\n"
    chunks = []
    size = 0
    while size < target_bytes:
        chunks.append(paragraph)
        size += len(paragraph.encode("utf-8"))
    return "".join(chunks)


def _bench(label: str, markdown: str) -> dict[str, float]:
    sys.path.insert(0, str(ROOT / "src"))
    from md2docx.parser.markdown_parser import MarkdownParser
    from md2docx.elements import create_default_registry
    from md2docx.processor.ast_processor import AstProcessor
    from md2docx.processor.context import ProcessingContext
    from md2docx.ooxml.package import DocxPackageWriter

    tracemalloc.start()
    t0 = time.perf_counter()
    ast = MarkdownParser().parse(markdown)
    t1 = time.perf_counter()
    context = ProcessingContext.create_default()
    AstProcessor(create_default_registry()).process_document(ast, context)
    t2 = time.perf_counter()
    out = OUT / f"bench-{label}.docx"
    DocxPackageWriter().write_from_context(context, out)
    t3 = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "parse_s": t1 - t0,
        "process_s": t2 - t1,
        "package_s": t3 - t2,
        "total_s": t3 - t0,
        "peak_mb": peak / (1024 * 1024),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sizes = {
        "10kb": 10 * 1024,
        "100kb": 100 * 1024,
        "1mb": 1024 * 1024,
    }
    lines = ["# Performance baseline", "", "| Size | parse | process | package | total | peak MB |", "|------|-------|---------|---------|-------|---------|"]
    for label, nbytes in sizes.items():
        stats = _bench(label, _synthetic_markdown(nbytes))
        lines.append(
            f"| {label} | {stats['parse_s']:.3f}s | {stats['process_s']:.3f}s | "
            f"{stats['package_s']:.3f}s | {stats['total_s']:.3f}s | {stats['peak_mb']:.1f} |"
        )
        print(f"{label}: total {stats['total_s']:.3f}s peak {stats['peak_mb']:.1f} MB")
    report = "\n".join(lines) + "\n"
    (OUT / "BENCHMARK.md").write_text(report, encoding="utf-8")
    print(f"Report → {OUT / 'BENCHMARK.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
