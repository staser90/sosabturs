#!/usr/bin/env python3
"""
Audit i18n coverage for Django templates and locale files.

Goals:
- Extract msgids used via {% trans "..." %} and {% blocktrans %} (basic).
- Detect likely hardcoded human text in templates (best-effort heuristic).
- Verify every used msgid exists in every locale/*/LC_MESSAGES/django.po.

Usage:
  python scripts/i18n_audit.py            # prints report, exit 1 if missing
  python scripts/i18n_audit.py --no-fail  # prints report, exit 0
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# Only public site templates (avoid emails/admin app templates).
TEMPLATES_DIRS = [ROOT / "templates"]
LOCALE_DIR = ROOT / "locale"
LOCALES = ["en", "es", "fr", "it"]  # enforce non-PT locales


TRANS_RE = re.compile(r"""\{%\s*trans\s+["'](?P<msg>[^"']+)["']\s*%}""")
BLOCKTRANS_RE = re.compile(r"""\{%\s*blocktrans\b[\s\S]*?%}(?P<body>[\s\S]*?)\{%\s*endblocktrans\s*%}""")

# Very rough: strip template tags/vars and look for letters left behind.
TAG_RE = re.compile(r"(\{[%#].*?[%#]\}|\{\{.*?\}\})", re.S)
HTML_TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def parse_po(path: Path) -> dict[str, str]:
    """
    Minimal .po parser for singular msgid/msgstr (keeps header too).
    """
    entries: dict[str, str] = {}
    msgid_parts: list[str] | None = None
    msgstr_parts: list[str] | None = None
    state: str | None = None
    fuzzy = False

    def unq(line: str) -> str:
        line = line.strip()
        if not line.startswith('"'):
            return ""
        # PO strings use C-style escapes; Python literal_eval matches well.
        return ast.literal_eval(line)

    def flush():
        nonlocal msgid_parts, msgstr_parts, state, fuzzy
        if msgid_parts is None or msgstr_parts is None:
            msgid_parts = msgstr_parts = state = None
            fuzzy = False
            return
        if fuzzy:
            msgid_parts = msgstr_parts = state = None
            fuzzy = False
            return
        msgid = "".join(msgid_parts)
        msgstr = "".join(msgstr_parts)
        entries[msgid] = msgstr
        msgid_parts = msgstr_parts = state = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("#,") and "fuzzy" in line:
            fuzzy = True
            continue
        if line.startswith("#~"):
            continue
        if line.startswith("msgid "):
            flush()
            state = "msgid"
            msgid_parts = [unq(line[len("msgid ") :])]
            msgstr_parts = []
            continue
        if line.startswith("msgstr "):
            state = "msgstr"
            if msgstr_parts is None:
                msgstr_parts = []
            msgstr_parts.append(unq(line[len("msgstr ") :]))
            continue
        if line.startswith('"'):
            if state == "msgid" and msgid_parts is not None:
                msgid_parts.append(unq(line))
            elif state == "msgstr" and msgstr_parts is not None:
                msgstr_parts.append(unq(line))
            continue
    flush()
    return entries


def iter_template_files() -> list[Path]:
    files: list[Path] = []
    for d in TEMPLATES_DIRS:
        if d.exists():
            files.extend(d.rglob("*.html"))
            files.extend(d.rglob("*.txt"))
    # Exclude admin override templates (optional scope)
    files = [f for f in files if "/templates/admin/" not in str(f)]
    return sorted(set(files))


def extract_msgids_from_template(text: str) -> set[str]:
    msgids: set[str] = set()
    for m in TRANS_RE.finditer(text):
        msgids.add(m.group("msg").strip())
    for m in BLOCKTRANS_RE.finditer(text):
        body = WS_RE.sub(" ", m.group("body").strip())
        # Keep body if it has letters and isn't empty. This is imperfect but useful.
        if any(ch.isalpha() for ch in body):
            msgids.add(body)
    return msgids


def find_suspect_hardcoded_text(text: str) -> list[str]:
    """
    Heuristic: lines that contain visible letters after stripping tags/vars.
    """
    suspects: list[str] = []
    in_style = False
    in_script = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "<style" in line:
            in_style = True
        if "</style" in line:
            in_style = False
            continue
        if "<script" in line:
            in_script = True
        if "</script" in line:
            in_script = False
            continue
        if in_style or in_script:
            continue
        # ignore obvious non-human lines
        if line.startswith(("{%","{{","<script","</script","<style","</style","//","/*","*")):
            continue
        cleaned = TAG_RE.sub("", line)
        cleaned = HTML_TAG_RE.sub(" ", cleaned)
        cleaned = WS_RE.sub(" ", cleaned).strip()
        if not cleaned:
            continue
        # ignore pure symbols/numbers
        if not any(ch.isalpha() for ch in cleaned):
            continue
        # ignore if it is exactly one of the language switch flags/codes
        if cleaned in {"PT", "EN", "ES", "FR", "IT"}:
            continue
        # ignore if line already contains a trans/blocktrans tag
        if "{% trans" in line or "{% blocktrans" in line:
            continue
        suspects.append(cleaned[:160])
    return suspects


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fail", action="store_true")
    args = ap.parse_args()

    template_files = iter_template_files()
    used_msgids: set[str] = set()
    hardcoded: dict[str, list[str]] = {}

    for f in template_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        used_msgids |= extract_msgids_from_template(text)
        sus = find_suspect_hardcoded_text(text)
        if sus:
            hardcoded[str(f.relative_to(ROOT))] = sus[:25]

    po_by_locale: dict[str, dict[str, str]] = {}
    for loc in LOCALES:
        po = LOCALE_DIR / loc / "LC_MESSAGES" / "django.po"
        if po.exists():
            po_by_locale[loc] = parse_po(po)
        else:
            po_by_locale[loc] = {}

    missing: dict[str, list[str]] = {}
    for loc, entries in po_by_locale.items():
        miss = sorted(m for m in used_msgids if m not in entries)
        if miss:
            missing[loc] = miss

    print("\n== i18n audit ==")
    print(f"Templates scanned: {len(template_files)}")
    print(f"Msgids found via trans/blocktrans: {len(used_msgids)}")
    for loc in LOCALES:
        count = len(po_by_locale.get(loc, {}))
        miss = len(missing.get(loc, []))
        print(f"- {loc}: {count} entries, missing {miss}")

    if hardcoded:
        print("\n== Suspect hardcoded text (needs wrapping in {% trans %} / {% blocktrans %}) ==")
        for fp, lines in list(hardcoded.items())[:20]:
            print(f"\n{fp}")
            for s in lines:
                print(f"  - {s}")
        if len(hardcoded) > 20:
            print(f"\n... and {len(hardcoded) - 20} more files")

    if missing:
        print("\n== Missing msgids per locale ==")
        for loc, miss in missing.items():
            print(f"\n{loc} missing ({len(miss)}):")
            for m in miss[:80]:
                print(f"  - {m}")
            if len(miss) > 80:
                print(f"  ... and {len(miss) - 80} more")

    if missing and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

