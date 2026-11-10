"""Generate the fictional Equity Splits example files in the instructor's formats.

Run from the repo root, after make_examples.py, make_baseline_example.py and make_salary_examples.py:

    python negotiation_agent/examples/tools/make_equity_examples.py

Writes, under negotiation_agent/examples/:
  BUS 4489 F26 Roster - Equity Splits prepared.xlsx   after Salary: Mia Underwood has dropped, gender and consent are
                                                       recorded, and an ES tab is prepared (headers, team numbers)
  BUS 4489 F26 Roster - Equity Splits in class.xlsx   the same, drafted and with the final teams after three absences
                                                       (made by the negotiation-pairing skill itself)
  BUS 4489 F26 Equity Splits Process Points (Responses) - Form Responses 1.csv
                                                       the in-class Google Form, downloaded as CSV
  expected/equity.json                                 the planted cases and what the skills should do with them

Every name and answer is fictional. The planted problems mirror the ones in her real Week 4 sheet.
"""
from __future__ import annotations

import csv
import json
import random
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent
AGENT = EXAMPLES.parent
sys.path.insert(0, str(AGENT / "shared"))
import nps_shared as ns  # noqa: E402

SALARY = "BUS 4489 F26 Roster - Salary in class.xlsx"
BASELINE_CSV = "BUS+4489+F26+Week+1+-+Negotiation+Baseline+Survey_September+30,+2026_09.44.csv"
PREPARED = "BUS 4489 F26 Roster - Equity Splits prepared.xlsx"
IN_CLASS = "BUS 4489 F26 Roster - Equity Splits in class.xlsx"
FORM_CSV = "BUS 4489 F26 Equity Splits Process Points (Responses) - Form Responses 1.csv"
DROPPED = "Underwood, Mia"
EVANS = "R_base0009=Evans, Jordan"
ROLES = ["MICHAEL", "PHUC", "GEORG"]
FORM_HEADER = [
    "Timestamp", "TRIO: What is your trio number?", "OBSERVER: What is your first name?",
    "OBSERVER: What is your last name?", "OBSERVER: What was your role in this negotiation?",
    "PARTNER: What is the first name of the person you are assessing?",
    "PARTNER: What is the last name of the person you are assessing?",
    "PARTNER: What was the role of the person you are assessing?",
    "1) TRUST: How much do you trust this person? (debrief question)",
    "2) RESPECT: How much respect did this person give you for the value you bring to the deal? (debrief question)",
    "3) FAIRNESS: How equitable do you believe the process was? (debrief question)",
    "4) INTERESTS: How much did this person attempt to understand your interests? (debrief question)",
    "5) FUTURE: How interested are you in working with this person in the future? (debrief question)",
]


def add_es_tab(wb) -> None:
    """The ES tab prepared the way she prepares the others: three roles, each with Email and the earlier codes."""
    ws = wb.create_sheet("ES")
    ids = ["UC", "SL", "ES"]
    ws.append(["MATCH"] + [x for r in ROLES for x in (r, "Email", *ids)])
    for i in range(1, 19):
        ws.cell(i + 1, 1, i)
    ws.cell(24, 1, "MATCH")
    for k, r in enumerate(ROLES):
        ws.cell(24, 2 + k, r)
    for i in range(1, 19):
        ws.cell(24 + i, 1, i)
    for k in range(3):
        ws.column_dimensions["BGL"[k]].width = 22


def make_rosters(folder: Path) -> dict:
    script = AGENT / "skills" / "negotiation-pairing" / "scripts" / "pairing.py"

    def run(*args):
        out = subprocess.run([sys.executable, str(script), *args], cwd=folder, capture_output=True, text=True)
        result = json.loads(out.stdout)
        assert result["ok"], result
        return result

    shutil.copy(EXAMPLES / SALARY, folder / PREPARED)
    shutil.copy(EXAMPLES / BASELINE_CSV, folder / BASELINE_CSV)
    wb = load_workbook(folder / PREPARED)
    att = wb["Att - Fall"]
    att.delete_rows(next(c.row for c in att["B"] if c.value == DROPPED))
    add_es_tab(wb)
    wb.save(folder / PREPARED)
    run("write-baseline", "--roster", PREPARED, "--csv", BASELINE_CSV, "--assign", EVANS)
    shutil.copy(folder / PREPARED, EXAMPLES / PREPARED)
    shutil.copy(folder / PREPARED, folder / IN_CLASS)
    draft = run("write-draft", "--roster", IN_CLASS, "--simulation", "ES", "--accept-warnings")
    run("roles-sent", "--roster", IN_CLASS, "--simulation", "ES")
    teams = {m["match"]: m for m in draft["draft"]}
    four = [m for m, t in teams.items() if sum(len(t[r]) for r in ROLES) == 4]
    regular = [m for m in sorted(teams) if m not in four]
    # Three absences: two are filled by the two extras; the third leaves a team that must be merged.
    absent = [teams[regular[0]]["MICHAEL"][0], teams[regular[3]]["GEORG"][0], teams[regular[6]]["PHUC"][0]]
    proposal = run("absences", "--roster", IN_CLASS, "--simulation", "ES", *sum((["--absent", a] for a in absent), []))
    final = run("write-final", "--roster", IN_CLASS, "--simulation", "ES", *sum((["--absent", a] for a in absent), []),
                "--accept-warnings")
    shutil.copy(folder / IN_CLASS, EXAMPLES / IN_CLASS)
    return {"draft": draft["draft"], "four_person_teams": four, "absent": absent, "moves": proposal["moves"],
            "final": final["final"]}


def split(name: str) -> tuple[str, str]:
    first, last = ns.split_class_name(name)
    return first, last


def make_form(final: list[dict]) -> dict:
    """Every student rates every teammate, with the kinds of problems in her Week 4 export."""
    rng = random.Random(44)
    rows, planted = [], {}
    when = datetime(2026, 11, 5, 17, 36, 0)
    teams = [(m["match"], [(n, r) for r in ROLES for n in m[r]]) for m in final]
    skip = {(teams[2][1][0][0], teams[2][1][1][0])}            # one rating never submitted
    planted["missing_rating"] = {"observer": teams[2][1][0][0], "partner": teams[2][1][1][0]}
    for match, members in teams:
        for observer, o_role in members:
            for partner, p_role in members:
                if observer == partner or (observer, partner) in skip:
                    continue
                o_first, o_last = split(observer)
                p_first, p_last = split(partner)
                scores = [rng.choice([2, 3, 3, 4, 4, 4, 5, 5]) for _ in range(5)]
                rows.append([when.strftime("%Y-%m-%d %H:%M:%S"), str(match), o_first, o_last, o_role.title(),
                             p_first, p_last, p_role.title(), *scores])
                when += timedelta(seconds=rng.randint(5, 70))
    rng.shuffle(rows)
    rows.sort(key=lambda r: r[0])
    for i, r in enumerate(rows):   # timestamps in submission order, as in her export
        r[0] = (datetime(2026, 11, 5, 17, 36, 0) + timedelta(seconds=40 * i)).strftime("%Y-%m-%d %H:%M:%S")

    def pick(test):
        return next(r for r in rows if test(r))

    r = pick(lambda r: r[1] == str(teams[0][0]))
    r[1] = f"#{r[1]}"
    planted["trio_hash"] = {"observer": f"{r[3]}, {r[2]}", "typed": r[1]}
    r = pick(lambda r: r[1] == str(teams[1][0]) and r[7] != r[4])
    r[4] = r[7]   # the observer typed their partner's role as their own, as in her sheet
    planted["wrong_role"] = {"observer": f"{r[3]}, {r[2]}", "typed": r[4]}
    r = pick(lambda r: r[1] == str(teams[3][0]) and len(r[6]) > 3)
    planted["misspelled_partner"] = {"partner": f"{r[6]}, {r[5]}", "typed": r[6][:-1]}
    r[6] = r[6][:-1]   # a misspelled last name, as in her sheet
    r = pick(lambda r: r[1] == str(teams[4][0]))
    r[2], r[3], r[5] = r[2].lower() + " ", r[3].lower(), r[5] + " "   # lowercase, trailing spaces
    planted["lowercase"] = {"observer": f"{r[3].title()}, {r[2].strip().title()}"}
    r = pick(lambda r: r[1] == str(teams[5][0]))
    r[11] = "6"   # out of range
    planted["out_of_range"] = {"observer": f"{r[3]}, {r[2]}", "partner": f"{r[6]}, {r[5]}", "value": 6}
    r = pick(lambda r: r[1] == str(teams[6][0]))
    dup = list(r)
    dup[0] = (datetime.strptime(rows[-1][0], "%Y-%m-%d %H:%M:%S") + timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
    dup[8] = "1" if r[8] != "1" else "2"
    rows.append(dup)   # submitted twice: the later one is used
    planted["duplicate"] = {"observer": f"{r[3]}, {r[2]}", "partner": f"{r[6]}, {r[5]}", "used_trust": int(dup[8])}
    r = pick(lambda r: r[1] == str(teams[7][0]))
    r[1] = str(teams[8][0])   # wrong trio number; the names point to the right one
    planted["wrong_trio"] = {"observer": f"{r[3]}, {r[2]}", "typed": r[1], "actual": teams[7][0]}
    with (EXAMPLES / FORM_CSV).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FORM_HEADER)
        w.writerows(rows)
    planted["responses"] = len(rows)
    return planted


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        roster = make_rosters(Path(tmp))
    planted = make_form(roster["final"])
    (EXAMPLES / "expected" / "equity.json").write_text(
        json.dumps({"dropped": DROPPED, **roster, "form": planted}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"Wrote {PREPARED}, {IN_CLASS}, {FORM_CSV} and expected/equity.json")


if __name__ == "__main__":
    main()
