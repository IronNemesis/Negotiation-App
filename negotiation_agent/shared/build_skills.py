"""Copy the shared module into each skill's scripts/ folder.

Each skill must work on its own when zipped and uploaded, so it carries its own
copy of nps_shared.py. Edit the shared file in negotiation_agent/shared/ only,
then run:

    python negotiation_agent/shared/build_skills.py

Use --check to verify the copies are current without changing anything (exit
code 1 if any copy is out of date).
"""
from __future__ import annotations

import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parent / "nps_shared.py"
SKILLS = Path(__file__).resolve().parent.parent / "skills"
BANNER = ("# GENERATED COPY: do not edit here. Edit negotiation_agent/shared/nps_shared.py\n"
          "# and run negotiation_agent/shared/build_skills.py to update every skill.\n")


def main() -> int:
    check = "--check" in sys.argv
    source = BANNER + SHARED.read_text(encoding="utf-8")
    skill_dirs = sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").exists()) if SKILLS.exists() else []
    if not skill_dirs:
        print(f"No skills found under {SKILLS}.")
        return 0
    stale = []
    for skill in skill_dirs:
        target = skill / "scripts" / "nps_shared.py"
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == source:
            print(f"up to date: {skill.name}")
            continue
        stale.append(skill.name)
        if check:
            print(f"OUT OF DATE: {skill.name}")
        else:
            target.parent.mkdir(exist_ok=True)
            target.write_text(source, encoding="utf-8")
            print(f"updated: {skill.name}")
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
