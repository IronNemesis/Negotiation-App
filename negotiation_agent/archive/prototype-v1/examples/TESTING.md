# Testing with the Example Files

Everything in this folder is fictional. Names, student IDs, phone numbers, and links are made up, and every email address uses `@example.edu`, so a mail merge test cannot reach a real person.

## What's Here

```
examples/
├── Negotiation Pairing Solution/          ← point the agent at this folder
│   ├── Simulation Settings.xlsx           Used Car and Job Offer
│   ├── Templates/
│   │   └── Used Car Outcomes Template.xlsx  Surplus column has formulas; Final Price is left for class
│   ├── Fall 2026 Section 01/              27 roster rows, 2 past negotiations
│   │   ├── Roster.xlsx
│   │   ├── Pairing History.xlsx
│   │   └── Backups/
│   └── Fall 2026 Section 02/              12 students, no history yet
│       ├── Roster.xlsx
│       ├── Pairing History.xlsx
│       └── Backups/
└── test_tools/
    ├── make_fake_survey.py                builds a Qualtrics-style export for Stage 2
    └── check_pairing.py                   independent check of any pairing the agent makes
```

The Pairing History follows one guess at the instructor's layout: a title row, then one row per student with a Pair ID column and a Role column for each past negotiation. Pair IDs look like `N1-04` (negotiation 1, pair 4). Replace this file once you have a copy of her real spreadsheet.

## Edge Cases Built Into Section 01

| Student | Situation | What the agent should do |
|---|---|---|
| Alex Kim, Alex Rivera | Two students named Alex | "Alex is absent" goes to H2 instead of guessing |
| Katherine Nguyen | Goes by Katie (in Status Notes) | "Katie Nguyen is absent" goes to H2 with Katherine suggested |
| Liam Brennan | No student ID (late add) | Excluded from pairing and listed |
| Rohan Patel | Status "Dropped," but appears in Pairing History | Excluded from pairing and listed as "in history, not enrolled"; his past pairings still count |
| Chidi Okafor | No email address | Paired normally; marked "Missing email" in the mail merge workbook |
| Sofia Delgado | Student ID starts with 0 (`051230984`) | Leading zero kept everywhere; still matched when the survey drops it |
| Kwame Mensah, Declan O'Brien, Grace Chen | Were a group of three in the 10/1 negotiation | None of the three may be paired with each other |
| Alex Kim | Was absent on 10/1 | Has only one past partner |

25 students are pairable: 27 roster rows, minus Liam (no ID) and Rohan (dropped). With nobody absent, the count is odd and H3 should trigger. With one absence, it is even.

## Test Scenarios

Start every test from a fresh copy of `Negotiation Pairing Solution/` (copy the folder, or run `git checkout -- .` and `git clean -fd` inside `examples/`), because the agent writes to these files.

| # | Ask the agent | Expected |
|---|---|---|
| 1 | "Pair Fall 2026 Section 01 for Used Car. Mateo Flores is absent." | 24 students in 12 pairs, one Buyer and one Seller per pair, no repeats. Liam and Rohan are listed as excluded. Roles favor whoever had the other role on 9/24. |
| 2 | "Pair Section 01 for Used Car. Alex is absent." | H2: asks which Alex. Nothing is paired until you answer. |
| 3 | "Pair Section 01 for Used Car. Katie Nguyen is absent." | H2: suggests Katherine Nguyen; does not apply it on its own. |
| 4 | "Pair Section 01 for Used Car. Nobody is absent." | H3: asks you to choose a group of three, partnering a student yourself, or an observer. |
| 5 | After a draft exists, open `Pairing Draft.xlsx`, make Alex Kim and Chidi Okafor partners, save, and say "re-check my edits." | T4 flags a repeat (they share `N1-04`) and keeps your edit. Approval requires you to confirm the warning. |
| 6 | Approve a draft. | A backup appears in `Backups/`. `Pairing History.xlsx` gains `<M/D> Used Car Pair ID` and `<M/D> Used Car Role` columns, with new IDs continuing the `N3-01` pattern. `Role Mail Merge.xlsx` is created, and Chidi is marked "Missing email." |
| 7 | "Pair Fall 2026 Section 02 for Used Car." | 12 students and 6 pairs, unaffected by Section 01's history. |
| 8 | After scenario 6, run `make_fake_survey.py` (below), then say "Build the outcomes workbook for Section 01 Used Car." | H6: one duplicate and one unknown ID (the mistyped one, with the right student suggested). The preview response is ignored, and two students are marked "No response." Sofia is matched despite the missing zero. `Outcomes.xlsx` has partners on adjacent rows, the Surplus formulas are intact, and Final Price is blank. Total time should be under 10 minutes. |
| 9 | Run scenario 8 a second time. | The first `Outcomes.xlsx` is moved to `Backups/` before the new one is written. |
| 10 | "Build the outcomes workbook for Section 01 Job Offer." | H1: no approved pairing and no outcomes template; nothing is produced. |
| 11 | Rename the `Student ID` column in `Roster.xlsx`, then ask for a pairing. | H1: names the missing column; nothing is produced. |
| 12 | Leave `Pairing History.xlsx` open in Excel while approving (Windows). | The agent asks you to close it and retries once. It does not fail silently. |

## Test Tools

Both scripts need Python 3 with `openpyxl` (`pip install openpyxl`).

To check any pairing independently of the agent's own Checks sheet:

```bash
python test_tools/check_pairing.py "Negotiation Pairing Solution/Fall 2026 Section 01" "Negotiation Pairing Solution/Fall 2026 Section 01/<simulation folder>"
```

It lists who is missing, anyone duplicated or not on the roster, pairs without both roles, repeat partners, and whether the pairing has been recorded in Pairing History. Run it before and after approval.

To create a survey export for Stage 2, run this after a pairing is approved:

```bash
python test_tools/make_fake_survey.py "Negotiation Pairing Solution/Fall 2026 Section 01/<simulation folder>"
```

It writes `Survey Export.csv` in Qualtrics' three-header-row format and prints the exceptions it planted, so you know what the agent should catch.
