"""Inline astroorbit/core.py into web/template.html -> web/index.html.

Run after every change to the core so the browser version stays in sync:
    python build_web.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent
core = (ROOT / "astroorbit" / "core.py").read_text(encoding="utf-8")
template = (ROOT / "web" / "template.html").read_text(encoding="utf-8")

if "</script" in core.lower():
    raise SystemExit("core.py contains '</script', which would break the inline embed")

# <script> content is raw text (no entity decoding), so the code goes in verbatim
out = template.replace("__CORE_PY__", core)
(ROOT / "web" / "index.html").write_text(out, encoding="utf-8")
print(f"wrote web/index.html ({len(out) // 1024} KB)")
