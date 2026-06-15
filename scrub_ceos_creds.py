#!/usr/bin/env python3
"""
scrub_ceos_creds.py - Replace hardcoded admin/admin cEOS creds in scripts/*.py
with os.environ[...] lookups, so no lab credentials live in the (public) repo.

SAFE BY DEFAULT: dry-run. Shows a diff of what *would* change and writes nothing.
Add --apply to actually rewrite files (originals saved alongside as <file>.bak).

Role-aware - keys off the field name, not the value, so username/password/secret
(all "admin" in this lab) don't get crossed:
    username -> os.environ["cEOS_USER"]
    password -> os.environ["cEOS_PASS"]
    secret   -> os.environ["cEOS_PASS"]   (enable secret == password in this lab)
    auth=("admin","admin") -> auth=(os.environ["cEOS_USER"], os.environ["cEOS_PASS"])

Set these in your shell (or a gitignored .env) before running the scripts:
    export cEOS_USER='admin'
    export cEOS_PASS='admin'

Usage:
    python3 scrub_ceos_creds.py            # dry-run: print diffs, write nothing
    python3 scrub_ceos_creds.py --apply    # write changes, save <file>.bak first
"""
import re
import sys
import difflib
from pathlib import Path

SCRIPTS_DIR = Path("scripts")
USER = 'os.environ["cEOS_USER"]'
PASS = 'os.environ["cEOS_PASS"]'

# (regex, replacement). Each regex keeps the field-name + separator in the
# capture group(s) and swaps ONLY the "admin" literal.
SUBS = [
    # dict style:   "username": "admin"   /   'username':'admin'
    (re.compile(r'''(["']username["']\s*:\s*)["']admin["']'''), r'\1' + USER),
    (re.compile(r'''(["']password["']\s*:\s*)["']admin["']'''), r'\1' + PASS),
    (re.compile(r'''(["']secret["']\s*:\s*)["']admin["']'''),   r'\1' + PASS),
    # kwarg style:  username="admin"   /   username = "admin"
    (re.compile(r'''(\busername\s*=\s*)["']admin["']'''), r'\1' + USER),
    (re.compile(r'''(\bpassword\s*=\s*)["']admin["']'''), r'\1' + PASS),
    (re.compile(r'''(\bsecret\s*=\s*)["']admin["']'''),   r'\1' + PASS),
    # tuple style:  auth=("admin", "admin")
    (re.compile(r'''(\bauth\s*=\s*\(\s*)["']admin["'](\s*,\s*)["']admin["'](\s*\))'''),
     r'\1' + USER + r'\2' + PASS + r'\3'),
]


def ensure_import_os(text):
    """Add `import os` if we introduced os.environ and it's not already imported.
    Inserts after a shebang line if present, so the shebang stays on line 1."""
    if re.search(r'^\s*import os\b', text, re.M):
        return text
    lines = text.splitlines(keepends=True)
    at = 1 if lines and lines[0].startswith("#!") else 0
    lines.insert(at, "import os\n")
    return "".join(lines)


def transform(text):
    new = text
    for rx, repl in SUBS:
        new = rx.sub(repl, new)
    if "os.environ" in new:
        new = ensure_import_os(new)
    return new


def main():
    apply = "--apply" in sys.argv
    if not SCRIPTS_DIR.is_dir():
        sys.exit("Run this from the repo root - no scripts/ dir found here.")

    changed = []
    for path in sorted(SCRIPTS_DIR.glob("*.py")):
        original = path.read_text()
        updated = transform(original)
        if updated == original:
            continue
        changed.append(path)
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=str(path), tofile=f"{path} (new)",
        )
        sys.stdout.write("".join(diff))
        if apply:
            path.with_name(path.name + ".bak").write_text(original)
            path.write_text(updated)

    print()
    if not changed:
        print("No admin/admin cEOS creds found - nothing to do.")
    elif apply:
        print(f"Applied to {len(changed)} file(s). Originals saved as *.py.bak")
    else:
        print(f"DRY-RUN: {len(changed)} file(s) would change. "
              f"Re-run with --apply to write them.")


if __name__ == "__main__":
    main()