#!/usr/bin/env python3
"""
Compile Django .po files into .mo without gettext/msgfmt.

Usage:
  python scripts/compile_mo.py
"""

from __future__ import annotations

import ast
import os
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIR = ROOT / "locale"


def _unquote_po_string(s: str) -> str:
    s = s.strip()
    if not s.startswith('"'):
        return ""
    # PO strings use C-style escapes; Python literal_eval matches well enough.
    return ast.literal_eval(s)


def parse_po(path: Path) -> dict[str, str]:
    """
    Minimal .po parser for singular msgid/msgstr.
    Skips fuzzy/obsolete entries and plurals.
    """
    entries: dict[str, str] = {}
    msgid_parts: list[str] | None = None
    msgstr_parts: list[str] | None = None
    state: str | None = None
    fuzzy = False

    def flush():
        nonlocal msgid_parts, msgstr_parts, state, fuzzy
        if fuzzy:
            msgid_parts = msgstr_parts = state = None
            fuzzy = False
            return
        if msgid_parts is None or msgstr_parts is None:
            msgid_parts = msgstr_parts = state = None
            return
        msgid = "".join(msgid_parts)
        msgstr = "".join(msgstr_parts)
        # Ignore header entry (empty msgid)
        if msgid:
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
            # obsolete
            continue
        if line.startswith("msgid_plural") or line.startswith("msgstr["):
            # skip plurals (not used in this project right now)
            state = "skip_plural"
            continue
        if state == "skip_plural":
            if line.startswith("msgid") or line.startswith("msgstr"):
                # let next state handle it
                state = None
            else:
                continue
        if line.startswith("msgid "):
            flush()
            state = "msgid"
            msgid_parts = [_unquote_po_string(line[len("msgid ") :])]
            msgstr_parts = []
            continue
        if line.startswith("msgstr "):
            state = "msgstr"
            if msgstr_parts is None:
                msgstr_parts = []
            msgstr_parts.append(_unquote_po_string(line[len("msgstr ") :]))
            continue
        if line.startswith('"'):
            if state == "msgid" and msgid_parts is not None:
                msgid_parts.append(_unquote_po_string(line))
            elif state == "msgstr" and msgstr_parts is not None:
                msgstr_parts.append(_unquote_po_string(line))
            continue

    flush()
    return entries


def build_mo(messages: dict[str, str]) -> bytes:
    """
    Build a GNU MO file (little endian).
    """
    # Sort by msgid
    items = sorted(messages.items(), key=lambda kv: kv[0])
    ids = b"\x00".join(k.encode("utf-8") for k, _ in items) + b"\x00"
    strs = b"\x00".join(v.encode("utf-8") for _, v in items) + b"\x00"

    keystart = 7 * 4 + len(items) * 8 * 2
    valuestart = keystart + len(ids)

    koffsets = []
    offset = 0
    for k, _ in items:
        b = k.encode("utf-8")
        koffsets.append((len(b), keystart + offset))
        offset += len(b) + 1

    voffsets = []
    offset = 0
    for _, v in items:
        b = v.encode("utf-8")
        voffsets.append((len(b), valuestart + offset))
        offset += len(b) + 1

    output = []
    # magic, version, nstrings, off_msgid_tbl, off_msgstr_tbl, hash size, hash offset
    output.append(struct.pack("<Iiiiiii", 0x950412de, 0, len(items), 7 * 4, 7 * 4 + len(items) * 8, 0, 0))
    for ln, off in koffsets:
        output.append(struct.pack("<ii", ln, off))
    for ln, off in voffsets:
        output.append(struct.pack("<ii", ln, off))
    output.append(ids)
    output.append(strs)
    return b"".join(output)


def compile_all():
    if not LOCALE_DIR.exists():
        raise SystemExit(f"Locale dir not found: {LOCALE_DIR}")

    po_files = list(LOCALE_DIR.glob("*/LC_MESSAGES/django.po"))
    if not po_files:
        raise SystemExit("No django.po files found.")

    for po in po_files:
        messages = parse_po(po)
        mo_bytes = build_mo(messages)
        mo_path = po.with_suffix(".mo")
        mo_path.write_bytes(mo_bytes)
        print(f"Wrote {mo_path.relative_to(ROOT)} ({len(messages)} msgs)")


if __name__ == "__main__":
    compile_all()

