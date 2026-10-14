"""Package each skill as a zip ready to upload to the Claude desktop app (Settings → Capabilities → Skills).

    python negotiation_agent/shared/package_skills.py

Checks first that every skill carries the current shared module and has a valid SKILL.md, then writes
dist/<skill name>.zip at the repo root, with the skill folder at the top of the zip (as the upload expects).
"""
from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent / "skills"
DIST = HERE.parent.parent / "dist"
SKIP = {"__pycache__", ".DS_Store"}


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit(f"{skill_md}: missing YAML frontmatter")
    fields = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    return fields


def main() -> int:
    if subprocess.run([sys.executable, str(HERE / "build_skills.py"), "--check"]).returncode:
        print("Run build_skills.py first: a skill has an out-of-date copy of the shared module.")
        return 1
    DIST.mkdir(exist_ok=True)
    for skill in sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").exists()):
        fields = frontmatter(skill / "SKILL.md")
        if fields.get("name") != skill.name:
            raise SystemExit(f"{skill.name}: SKILL.md name '{fields.get('name')}' must match the folder name")
        if not 0 < len(fields.get("description", "")) <= 1024:
            raise SystemExit(f"{skill.name}: description must be 1-1024 characters")
        target = DIST / f"{skill.name}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            for path in sorted(skill.rglob("*")):
                if path.is_file() and not SKIP & set(path.parts):
                    z.write(path, Path(skill.name) / path.relative_to(skill))
        with zipfile.ZipFile(target) as z:
            names = z.namelist()
        print(f"{target.relative_to(DIST.parent)}: {len(names)} files ({', '.join(names)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
