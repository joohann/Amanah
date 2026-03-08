#!/usr/bin/env python3
"""
Amanah — scripts/check_versions.py
Controleert of versienummers in manifest.json, const.py en CHANGELOG.md
allemaal overeenkomen. Wordt uitgevoerd als onderdeel van de CI pipeline.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

errors = []

# 1. Lees manifest.json
manifest = json.loads((ROOT / "custom_components/amanah/manifest.json").read_text())
manifest_version = manifest["version"]

# 2. Lees const.py
const_text = (ROOT / "custom_components/amanah/const.py").read_text()
match = re.search(r'^VERSION\s*=\s*"([^"]+)"', const_text, re.MULTILINE)
if not match:
    errors.append("❌ VERSION niet gevonden in const.py")
    const_version = None
else:
    const_version = match.group(1)

# 3. Lees CHANGELOG.md — eerste versie header
changelog_text = (ROOT / "CHANGELOG.md").read_text()
match = re.search(r"## \[(\d+\.\d+\.\d+)\]", changelog_text)
if not match:
    errors.append("❌ Geen versie gevonden in CHANGELOG.md")
    changelog_version = None
else:
    changelog_version = match.group(1)

# 4. Vergelijk
print(f"manifest.json  : {manifest_version}")
print(f"const.py       : {const_version}")
print(f"CHANGELOG.md   : {changelog_version}")

if const_version and const_version != manifest_version:
    errors.append(
        f"❌ const.py ({const_version}) ≠ manifest.json ({manifest_version})"
    )

if changelog_version and changelog_version != manifest_version:
    errors.append(
        f"❌ CHANGELOG.md ({changelog_version}) ≠ manifest.json ({manifest_version})"
    )

if errors:
    print("\nVersie fouten gevonden:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)

print("\n✅ Alle versies zijn consistent!")
