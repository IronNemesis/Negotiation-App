"""Generate a fictional Week 1 baseline survey export in the instructor's exact format (number codes).

Run from the repo root, after make_examples.py:

    python negotiation_agent/examples/tools/make_baseline_example.py

Writes, under negotiation_agent/examples/:
  BUS+4489+F26+Week+1+-+Negotiation+Baseline+Survey_September+30,+2026_09.44.csv
  expected/baseline.json        what the skill should record for each student

Same columns and codes as her real baseline survey: Q1 consent (1 agree, 2 decline), Q11 first name, Q14 last name,
Q15 gender (1 Male, 2 Female, 4 Other with Q15_4_TEXT), then the research items, answered at random here.
The consent text is a short fictional stand-in.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent
sys.path.insert(0, str(HERE))
from make_examples import CLASS, sort_key  # noqa: E402
sys.path.insert(0, str(EXAMPLES.parent / "shared"))
from nps_shared import split_class_name  # noqa: E402

CSV_NAME = "BUS+4489+F26+Week+1+-+Negotiation+Baseline+Survey_September+30,+2026_09.44.csv"
META = ["StartDate", "EndDate", "Status", "IPAddress", "Progress", "Duration (in seconds)", "Finished",
        "RecordedDate", "ResponseId", "RecipientLastName", "RecipientFirstName", "RecipientEmail",
        "ExternalReference", "LocationLatitude", "LocationLongitude", "DistributionChannel", "UserLanguage"]
META_Q = ["Start Date", "End Date", "Response Type", "IP Address", "Progress", "Duration (in seconds)", "Finished",
          "Recorded Date", "Response ID", "Recipient Last Name", "Recipient First Name", "Recipient Email",
          "External Data Reference", "Location Latitude", "Location Longitude", "Distribution Channel",
          "User Language"]
ITEMS = ([f"Q5_{i}" for i in (1, 2, 3)] + ["Q7", "Q6", "Q8"] + [f"Q3_{i}" for i in range(1, 9)]
         + [f"Q9_{i}" for i in range(1, 13)] + [f"Q10_{i}" for i in range(1, 10)])
CODES = META + ["Q1", "Q11", "Q14", "Q15", "Q15_4_TEXT", "Q13"] + ITEMS
QUESTIONS = META_Q + [
    "INFORMED CONSENT TO PARTICIPATE IN A RESEARCH PROJECT\n\n(Fictional consent text for the example file.)\n\n"
    "PLEASE CLICK ON ONE OF THE FOLLOWING BUTTONS:",
    "What is your first name?", "What is your last name?", "What is your gender? - Selected Choice",
    "What is your gender? - Other - Text", "Select your age below:"] + [f"Research item {c}" for c in ITEMS]
IMPORT_IDS = ([f'{{"ImportId":"{x}"}}' for x in META]
              + ['{"ImportId":"QID1"}', '{"ImportId":"QID11_TEXT"}', '{"ImportId":"QID14_TEXT"}',
                 '{"ImportId":"QID15"}', '{"ImportId":"QID15_4_TEXT"}', '{"ImportId":"QID13"}']
              + [f'{{"ImportId":"QID{c[1:]}"}}' for c in ITEMS])

# Planted cases. Gender codes: 1 Male, 2 Female, 4 Other.
SPECIAL = {
    "Bennett, Owen": {"consent": "2", "expect": ("M", "No")},
    "Ortiz, Lena": {"consent": "2", "expect": ("F", "No")},
    "Hoang, Minh": {"gender": "4", "other": "Nonbinary", "expect": ("Other", "Excluded")},
    "Kowalski, Andy": {"first": "Andrew", "expect": ("M", "Yes")},
    "Rossi, Gianna": {"first": "gianna ", "last": "rossi ", "expect": ("F", "Yes")},
    "Evans, Jordan": {"last": "Evens", "expect": ("M", "Yes")},          # needs her confirmation
    "Sato, Hiro": {"duplicate": True, "expect": ("M", "Yes")},          # took it twice: the later one counts
}
NO_SURVEY = ["Underwood, Mia", "Walsh, Connor"]
FEMALE = {"Maya", "Rosa", "Priya", "Leah", "Nora", "Simone", "Lucia", "Camille", "Grace", "Katherine", "Siobhan",
          "Lena", "Danielle", "Ava", "Noor", "Gianna", "Elise", "Tess", "Mia"}


def main() -> None:
    rng = random.Random(1)
    rows, expected, n = [], {}, 0
    for name in sorted(CLASS, key=sort_key):
        first, last = split_class_name(name)
        if name in NO_SURVEY:
            expected[name] = ["", "No (no survey)"]
            continue
        spec = SPECIAL.get(name, {})
        gender = spec.get("gender", "2" if first in FEMALE else "1")
        consent = spec.get("consent", "1")
        expected[name] = list(spec.get("expect", ("F" if gender == "2" else "M", "Yes")))
        for k in range(2 if spec.get("duplicate") else 1):
            n += 1
            stamp = f"2026-09-30 09:{10 + n:02d}:{rng.randint(0, 59):02d}"
            answers = [str(rng.randint(1, 5)) for _ in ITEMS]
            row_consent = "2" if spec.get("duplicate") and k == 0 else consent   # changed their answer the 2nd time
            rows.append([stamp, stamp, "0", f"203.0.113.{n}", "100", str(rng.randint(150, 450)), "1", stamp,
                         f"R_base{n:04d}", "", "", "", "", "35.2865", "-120.6822", "anonymous", "EN", row_consent,
                         spec.get("first", first), spec.get("last", last), gender, spec.get("other", ""),
                         str(rng.randint(2, 6)), *answers])
    preview = ["2026-09-29 16:00:00"] * 2 + ["1", "", "100", "60", "1", "2026-09-29 16:01:00", "R_preview", "", "",
                                             "", "", "", "", "preview", "EN", "1", "Test", "Preview", "1", "", "3"]
    rows.insert(0, preview + ["3"] * len(ITEMS))
    with (EXAMPLES / CSV_NAME).open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerows([CODES, QUESTIONS, IMPORT_IDS, *rows])
    (EXAMPLES / "expected" / "baseline.json").write_text(
        json.dumps({"students": expected, "ask_about": ["Evans, Jordan"]}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"Baseline: {len(rows)} rows (1 preview), {len(NO_SURVEY)} students without a survey")


if __name__ == "__main__":
    main()
