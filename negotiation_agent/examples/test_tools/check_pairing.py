"""Independently check a pairing the agent produced.

Does not trust the agent's own Checks sheet. Reads the section's roster and
Pairing History plus the simulation's Pairing Draft.xlsx, and reports:
  - who from the roster is missing from the draft (compare against the absences you gave)
  - anyone in the draft twice, or not on the roster
  - groups that do not have one of each role
  - repeat partners (pairs who already share a pair ID in Pairing History)
  - whether this pairing has already been recorded in Pairing History (T5)

Usage:
    python check_pairing.py "<section folder>" "<simulation folder>"
"""
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from openpyxl import load_workbook


def table(path, must_have):
    rows = list(load_workbook(path, data_only=True).worksheets[0].iter_rows(values_only=True))
    for i, row in enumerate(rows):
        cells = [str(c).strip().lower() if c is not None else "" for c in row]
        if all(any(word in c for c in cells) for word in must_have):
            return cells, rows[i + 1:]
    sys.exit(f"No header row containing {must_have} found in {path}")


def col(cells, word, avoid=None):
    for i, c in enumerate(cells):
        if word in c and not (avoid and avoid in c):
            return i
    return None


def norm(sid):
    return str(sid).strip().lstrip("0") if sid is not None else ""


def main():
    section, sim = Path(sys.argv[1]), Path(sys.argv[2])

    cells, rows = table(section / "Roster.xlsx", ["student id"])
    sid_c, name_c, status_c = col(cells, "student id"), col(cells, "name"), col(cells, "status", avoid="note")
    roster = {}
    for r in rows:
        if r[sid_c] and (status_c is None or str(r[status_c]).strip().lower() == "enrolled"):
            name = str(r[name_c])
            roster[norm(r[sid_c])] = " ".join(reversed(name.split(",", 1))).strip() if "," in name else name

    hcells, rows = table(section / "Pairing History.xlsx", ["student id", "pair id"])
    hid_c = col(hcells, "student id")
    pair_cols = [i for i, c in enumerate(hcells) if "pair id" in c]
    history = {norm(r[hid_c]): {i: r[i] for i in pair_cols if r[i]} for r in rows if r[hid_c]}

    cells, rows = table(sim / "Pairing Draft.xlsx", ["id", "role"])
    did_c, role_c = col(cells, "id", avoid="partner"), col(cells, "role", avoid="partner")
    group_c = col(cells, "pair", avoid="partner")
    if group_c is None:
        group_c = col(cells, "group")
    if group_c is None:
        sys.exit("Could not find a pair or group number column in Pairing Draft.xlsx")
    groups, seen = defaultdict(list), defaultdict(int)
    for r in rows:
        if r[did_c]:
            sid = norm(r[did_c])
            groups[r[group_c]].append((sid, str(r[role_c] or "").strip()))
            seen[sid] += 1

    problems = 0
    missing = [roster[s] for s in roster if s not in seen]
    print(f"Draft: {sum(seen.values())} students in {len(groups)} groups. Enrolled with ID on roster: {len(roster)}.")
    print(f"Not in draft (should be exactly your absences, or an observer): {', '.join(missing) or 'none'}")
    for s, n in seen.items():
        if n > 1:
            problems += 1
            print(f"  ERROR: {roster.get(s, s)} appears {n} times")
        if s not in roster:
            problems += 1
            print(f"  ERROR: student ID {s} is not an enrolled roster student")

    # A pair-ID column where every draft group shares one value is this round, already recorded by T5.
    current = [c for c in pair_cols
               if all(len({history.get(s, {}).get(c) for s, _ in g}) == 1 and history.get(g[0][0], {}).get(c)
                      for g in groups.values() if len(g) > 1)]
    recorded = f"yes, column '{hcells[current[0]]}'" if current else "not yet"
    print(f"Recorded in Pairing History: {recorded}")

    for gid, members in groups.items():
        roles = [r for _, r in members]
        if len(members) == 2 and len(set(roles)) != 2:
            problems += 1
            print(f"  ERROR: group {gid} roles are {roles}")
        for (a, _), (b, _) in combinations(members, 2):
            shared = {v for c, v in history.get(a, {}).items() if c not in current} & \
                     {v for c, v in history.get(b, {}).items() if c not in current}
            if shared:
                problems += 1
                print(f"  REPEAT: {roster.get(a, a)} and {roster.get(b, b)} already share {', '.join(sorted(shared))}")

    print("PASS: no errors or repeat partners." if not problems else f"{problems} problem(s) found.")


if __name__ == "__main__":
    main()
