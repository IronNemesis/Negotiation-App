"""Generate the fictional Salary negotiation example files in the instructor's exact formats.

Run from the repo root, after make_examples.py:

    python negotiation_agent/examples/tools/make_salary_examples.py

Writes, under negotiation_agent/examples/:
  BUS 4489 F26 Roster - Salary in class.xlsx      UC done; SL drafted with her rotation, then the final matches
                                                    after one absence (made by the negotiation-pairing skill itself)
  BUS+4489+F26+Week+3+-+Salary+Bargaining+Range+SUPERVISOR_October+20,+2026_16.01.csv
  BUS+4489+F26+Week+3+-+Salary+Bargaining+Range+SUBORDINATE_October+20,+2026_16.01.csv
                                                    the two Qualtrics surveys students take before class
  BUS 4489 F26 Salary Negotiation (Responses) - Form Responses 1.csv
                                                    the in-class Google Form, downloaded as CSV
  expected/salary.json                              the planted cases and what the skill should do with them

Every name and answer is fictional, and the planted problems mirror the ones in her real S25 files.
"""
from __future__ import annotations

import csv
import json
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent
AGENT = EXAMPLES.parent
sys.path.insert(0, str(AGENT / "shared"))
import nps_shared as ns  # noqa: E402

AFTER_UC = "BUS 4489 F26 Roster - after Used Car.xlsx"
ROSTER = "BUS 4489 F26 Roster - Salary in class.xlsx"
SUP_CSV = "BUS+4489+F26+Week+3+-+Salary+Bargaining+Range+SUPERVISOR_October+20,+2026_16.01.csv"
SUB_CSV = "BUS+4489+F26+Week+3+-+Salary+Bargaining+Range+SUBORDINATE_October+20,+2026_16.01.csv"
FORM_CSV = "BUS 4489 F26 Salary Negotiation (Responses) - Form Responses 1.csv"
ABSENT = "Chen, Priya"
PLACE = "O'Neill, Siobhan=7"   # the previous match would repeat her Used Car partner, so she is placed by hand

META = ["StartDate", "EndDate", "Status", "IPAddress", "Progress", "Duration (in seconds)", "Finished",
        "RecordedDate", "ResponseId", "RecipientLastName", "RecipientFirstName", "RecipientEmail",
        "ExternalReference", "LocationLatitude", "LocationLongitude", "DistributionChannel", "UserLanguage"]
META_Q = ["Start Date", "End Date", "Response Type", "IP Address", "Progress", "Duration (in seconds)", "Finished",
          "Recorded Date", "Response ID", "Recipient Last Name", "Recipient First Name", "Recipient Email",
          "External Data Reference", "Location Latitude", "Location Longitude", "Distribution Channel",
          "User Language"]
META_IDS = ['{"ImportId":"startDate","timeZone":"America/Los_Angeles"}',
            '{"ImportId":"endDate","timeZone":"America/Los_Angeles"}', '{"ImportId":"status"}',
            '{"ImportId":"ipAddress"}', '{"ImportId":"progress"}', '{"ImportId":"duration"}',
            '{"ImportId":"finished"}', '{"ImportId":"recordedDate","timeZone":"America/Los_Angeles"}',
            '{"ImportId":"_recordId"}', '{"ImportId":"recipientLastName"}', '{"ImportId":"recipientFirstName"}',
            '{"ImportId":"recipientEmail"}', '{"ImportId":"externalDataReference"}',
            '{"ImportId":"locationLatitude"}', '{"ImportId":"locationLongitude"}',
            '{"ImportId":"distributionChannel"}', '{"ImportId":"userLanguage"}']
EMAIL_Q = ("4. What is your email address? (This will be used to immediately trigger an email with a summary of your "
           "responses to this survey. The email summary will come from instructor@example.edu. If you cannot find "
           "it, please look in your clutter or junk mail folder.)")
SURVEYS = {
    "SUPERVISOR": (["Q1", "Q2", "Q12", "Q13", "Q14", "Q17"],
                   ["What is your FIRST NAME?", "What is your LAST NAME?",
                    "1. What raise will you suggest to your subordinate to start the negotiation? (initial offer)",
                    "2. What is the ideal raise you would give this subordinate? (target price)",
                    "3.  What is the absolute highest raise you would offer before walking away and going with your "
                    "BATNA? (reservation price)", EMAIL_Q]),
    "SUBORDINATE": (["Q1", "Q2", "Q4", "Q5", "Q6", "Q17"],
                    ["What is your FIRST NAME?", "What is your LAST NAME?",
                     "1. What raise will you suggest to your boss to start the negotiation? (initial offer)",
                     "2. What is your ideal raise amount? (target price)",
                     "3. What is the absolute lowest raise you would accept before going with your BATNA? "
                     "(reservation price)", EMAIL_Q]),
}
FORM_HEADER = [
    "Timestamp", "MATCH: What is your match number?", "SUPERVISOR FIRST NAME: ", "SUPERVISOR LAST NAME:",
    "SUBORDINATE FIRST NAME:", "SUBORDINATE LAST NAME:",
    "SUPERVISOR INITIAL OFFER: What was your initial offer - the first number you offered out loud during today's "
    "negotiation?   (state in TOTAL SALARY AMOUNT)",
    "SUPERVISOR TARGET: What was your target RAISE going into this negotiation?  (state in TOTAL SALARY AMOUNT)",
    "BASE: What was the original base salary?", "RAISE: What is the amount of the RAISE you agreed upon?",
    "TOTAL: What is the total SALARY you agreed upon? (Base plus raise)",
    "SUBORDINATE TARGET: (state in TOTAL SALARY AMOUNT)",
    "SUBORDINATE INITIAL OFFER: What was the first number for salary spoken by the subordinate?  (state in TOTAL "
    "SALARY AMOUNT)",
    "Did the SUBORDINATE make a credible threat to walk away?", "How many minutes did you negotiate for?",
    "To what extent was THE SUPERVISOR'S approach collaborative or competitive? (The subordinate must answer this "
    "question)",
    "To what extent was THE SUBORDINATE'S approach collaborative or competitive? (The supervisor must answer this "
    "question)",
    "Any other terms of the agreement:"]
APPROACH = ["Very collaborative", "Collaborative", "Somewhat collaborative", "Neutral", "Somewhat competitive",
            "Competitive", "Very competitive"]

# Planted survey answers (initial, target, reservation) and what the skill should show (total salary).
SUP_SPECIAL = {
    "Alvarez, Maya": {"prices": ("0 (they already got the $3,500 bonus)", "$2,500", "$8,500"),
                      "expect": {"INITIAL": ["corrected", 60000], "TARGET": ["raise", 62500]}},
    "Bennett, Owen": {"prices": ("63,500", "66,000", "68,000"), "expect": {"INITIAL": ["total", 63500]}},
    "Dawson, Leah": {"prices": ("2,000", "$5000-$6000", "9000"), "expect": {"TARGET": ["unclear", "$5000-$6000"]}},
    "Delgado, Marco": {"prices": ("NA", "4,000", "7,500"), "expect": {"INITIAL": ["unclear", "NA"]}},
    "Kowalski, Andy": {"first": "Andrew", "email": "andrew.k@example.com"},
    "Evans, Jordan": {"duplicate": ("3,000", "6,000", "10,000"), "prices": ("1,000", "4,000", "8,000"),
                      "expect": {"INITIAL": ["raise", 61000]}},
}
SUB_SPECIAL = {
    "Mendes, Rafael": {"prices": ("17,500", "13,500", "12,000"), "expect": {"INITIAL": ["raise", 77500]}},
    "Nakamura, Ren": {"prices": ("$80,000", "$75,000", "$70,000"), "expect": {"RESERVATION": ["total", 70000]}},
    "Quinn, Ava": {"prices": ("75,000 salary", "72,000", "70,000"), "expect": {"INITIAL": ["unclear", "75,000 salary"]}},
    "Reyes, Noor": {"prices": ("18,000", "15,000", "7"), "expect": {"RESERVATION": ["corrected", 67000]}},
}
NO_RESPONSE = ["Fitzgerald, Nora", "Underwood, Mia"]


def fmt(rng: random.Random, value: int) -> str:
    return rng.choice([str(value), f"${value}", f"{value:,}", f"${value:,}"])


def make_roster() -> list[dict]:
    """Run the pairing skill itself: SL draft with her rotation, then one absence placed by hand."""
    script = AGENT / "skills" / "negotiation-pairing" / "scripts" / "pairing.py"
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(EXAMPLES / AFTER_UC, Path(tmp) / AFTER_UC)

        def run(*args):
            out = subprocess.run([sys.executable, str(script), *args, "--roster", AFTER_UC, "--simulation", "SL"],
                                 cwd=tmp, capture_output=True, text=True)
            result = json.loads(out.stdout)
            assert result["ok"], result
            return result

        run("write-draft", "--accept-warnings")
        run("roles-sent")
        final = run("write-final", "--absent", ABSENT, "--place", PLACE, "--accept-warnings")["final"]
        shutil.copy(Path(tmp) / AFTER_UC, EXAMPLES / ROSTER)
    return final


EMAILS: dict[str, str] = {}


def survey_rows(rng, role, people, final_role_of):
    rows, expected, n = [], {}, 0
    minute = 0
    for name in people:
        if name in NO_RESPONSE:
            expected[name] = {"response": "none"}
            continue
        spec = (SUP_SPECIAL if role == "SUPERVISOR" else SUB_SPECIAL).get(name, {})
        first, last = ns.split_class_name(name)
        email = spec.get("email", EMAILS[name])

        def one(prices, extra_minutes=0):
            nonlocal n, minute
            n += 1
            minute += rng.randint(7, 50) + extra_minutes
            day, mins = 19 + minute // (12 * 60), 9 * 60 + minute % (12 * 60)   # 9am-9pm, then the next day
            start = f"2026-10-{day:02d} {mins // 60:02d}:{mins % 60:02d}:{rng.randint(0, 59):02d}"
            end = f"2026-10-{day:02d} {mins // 60:02d}:{min(mins % 60 + 4, 59):02d}:{rng.randint(0, 59):02d}"
            rows.append([start, end, "0", f"198.51.100.{n}", "100", str(rng.randint(30, 900)), "1", end,
                         f"R_{role[:3].lower()}{n:04d}", "", "", "", "", "35.2865", "-120.6822", "anonymous", "EN",
                         spec.get("first", first), spec.get("last", last), *prices, email])

        if "duplicate" in spec:
            one(spec["duplicate"])
        if "prices" in spec:
            prices = spec["prices"]
        elif role == "SUPERVISOR":
            target = rng.choice(range(3000, 8001, 500))
            prices = (fmt(rng, rng.choice(range(0, target, 500))), fmt(rng, target),
                      fmt(rng, target + rng.choice(range(1500, 6001, 500))))
        elif rng.random() < 0.5:   # subordinates answer as a raise or as a total salary
            reservation = rng.choice(range(6000, 12001, 500))
            prices = tuple(fmt(rng, v) for v in (reservation + 6000, reservation + 3000, reservation))
        else:
            reservation = rng.choice(range(66000, 72001, 500))
            prices = tuple(fmt(rng, v) for v in (reservation + 8000, reservation + 4000, reservation))
        one(prices, extra_minutes=600 if "duplicate" in spec else 0)
        expected[name] = {"expect": spec.get("expect", {}), "duplicate": "duplicate" in spec}
    rows.sort(key=lambda r: r[7])
    return rows, expected


def write_survey(path, role, rows):
    codes, questions = SURVEYS[role]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(META + codes)
        w.writerow(META_Q + questions)
        w.writerow(META_IDS + [f'{{"ImportId":"QID{c[1:]}_TEXT"}}' for c in codes])
        w.writerows(rows)


def form_rows(rng, final):
    rows, expected = [], {}
    stamp = 17 * 60 + 40

    def add(row):
        nonlocal stamp
        stamp += rng.randint(0, 3)
        rows.append([f"10/20/2026 {stamp // 60}:{stamp % 60:02d}:{rng.randint(0, 59):02d}", *row])

    for m in final:
        match = m["match"]
        if match == 12:   # nobody in match 12 submitted the form
            expected[str(match)] = "no form row"
            continue
        sups, subs = m["SUPERVISOR"], m["SUBORDINATE"]
        sf, sl = (" and ".join(ns.split_class_name(n)[i] for n in sups) for i in (0, 1))
        bf, bl = (" and ".join(ns.split_class_name(n)[i] for n in subs) for i in (0, 1))
        base = 60000
        raise_ = rng.choice(range(4000, 14001, 250))
        values = {
            "match": str(match), "sup_initial": fmt(rng, base + rng.choice(range(2000, 5001, 500))),
            "sup_target": fmt(rng, base + rng.choice(range(5000, 8001, 500))), "base": fmt(rng, base),
            "raise": fmt(rng, raise_), "total": fmt(rng, base + raise_),
            "sub_target": fmt(rng, base + rng.choice(range(10000, 15001, 500))),
            "sub_initial": fmt(rng, base + rng.choice(range(15000, 22001, 500))),
            "threat": rng.choice(["Yes", "No"]), "minutes": str(rng.randint(6, 38)),
            "sup_app": rng.choice(APPROACH), "sub_app": rng.choice(APPROACH),
            "terms": rng.choice(["", "", "None", "Review again in 6 months", "Extra week of vacation"]),
        }
        note = None
        if match == 3:
            values.update(raise_="5,500", total="6550")
            values["raise"], values["total"] = "5,500", "6550"
            note = "total typo: base + raise is $65,500"
        if match == 5:
            values["raise"], values["total"] = "No Deal", "No Deal"
            note = "no deal"
        if match == 7:
            values["match"] = "7 + Siobhan O'Neill"
            note = "three-person match typed into the match number"
        if match == 9:
            values["minutes"], values["threat"] = "35 minutes", "a threat was made but was not received as credible"
            note = "minutes typed with a word"
        if match == 10:
            values["sup_initial"] = "None"
            note = "no supervisor initial offer"
        if match == 11:   # supervisor typed a raise instead of a total
            values["sup_initial"] = "3,000"
            note = "supervisor initial offer typed as a raise"
        row = [values["match"], sf, sl, bf, bl, values["sup_initial"], values["sup_target"], values["base"],
               values["raise"], values["total"], values["sub_target"], values["sub_initial"], values["threat"],
               values["minutes"], values["sup_app"], values["sub_app"], values["terms"]]
        add(row)
        if match == 1:    # both partners submitted; the later one typed a salary into the match number
            dup = list(row)
            dup[0] = "66000"
            dup[1], dup[2], dup[3], dup[4] = sf.lower(), sl.lower(), bf.lower(), bl.lower()
            dup[16] = "same as my partner's"
            add(dup)
            note = "submitted twice; the later row has 66000 as the match number"
        if note:
            expected[str(match)] = note
    return rows, expected


def main() -> None:
    final = make_roster()
    wb = load_workbook(EXAMPLES / ROSTER)
    tab = ns.read_sim_tab(wb, "SL", ["SUPERVISOR", "SUBORDINATE"])
    EMAILS.update({st.name: st.email for st in ns.read_class_list(wb)[1]})
    role_of = {m.name: m.role for m in tab.final_members + tab.absent}
    rng = random.Random(489)
    expected = {"final": final, "absent": [m.name for m in tab.absent], "surveys": {}}
    for role, path in (("SUPERVISOR", SUP_CSV), ("SUBORDINATE", SUB_CSV)):
        people = sorted((n for n, r in role_of.items() if r == role), key=ns.class_name_key)
        rows, exp = survey_rows(rng, role, people, role_of)
        write_survey(EXAMPLES / path, role, rows)
        expected["surveys"][role] = exp
    rows, exp = form_rows(rng, final)
    with (EXAMPLES / FORM_CSV).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FORM_HEADER)
        w.writerows(rows)
    expected["form"] = exp
    (EXAMPLES / "expected" / "salary.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n",
                                                        encoding="utf-8")
    print(f"SL final: {len(final)} matches; absent: {expected['absent']}; form rows: {len(rows)}")


if __name__ == "__main__":
    main()
