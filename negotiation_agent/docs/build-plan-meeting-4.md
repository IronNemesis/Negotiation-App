# Build Plan: Meeting 4 Changes

**Status:** Draft for Aidan's approval. Nothing below has been built.

Meeting 4 asked for three things: the Salary outcomes sheet, gender and consent from the baseline survey, and experimental conditions (I/C) for Used Car. The Salary sheet is the priority for the next meeting. Items built on an assumption are listed in [`open-questions.md`](open-questions.md) for Aidan to confirm with her.

Her real files (the S25 roster data, the Qualtrics and Form exports, the baseline survey) are used only locally to check formats. Everything committed uses fictional students in the same formats.

## Order and Checkpoints

| Phase | What | Ready for the meeting? | Checkpoint |
|---|---|---|---|
| 1 | Salary outcomes sheet | Yes: the priority | Push after tests pass, then a dry run on her S25 files locally |
| 2 | Gender and consent from the baseline survey | Likely | Push after tests pass |
| 3 | I/C conditions in Used Car drafting, four BCC lists, absences | Only if 1 and 2 are done; otherwise shown as a plan | Push after tests pass |

## Phase 1: Salary Outcomes Sheet (`bargaining-range-sheet`)

**What she does in class:** downloads the Google Form responses as a CSV, then asks Claude to build the Salary outcomes sheet. Claude reads that CSV, the two Qualtrics exports from before class (Supervisor and Subordinate), and the `SL` tab of her roster for the matches (the final table if it has names, otherwise the draft).

**The sheet** follows her template, one row per match:

| Side | Columns |
|---|---|
| Supervisor (left) | MATCH, FIRST, LAST, ACTUAL INITIAL (Form), INITIAL OFFER, TARGET, RESERVATION (Qualtrics) |
| Middle (Form) | BASE, RAISE, TOTAL |
| Subordinate (right, mirrored) | RESERVATION, TARGET, INITIAL OFFER (Qualtrics), ACTUAL INITIAL (Form), FIRST, LAST |
| After (Form) | Credible threat to walk away, minutes, each side's approach, other terms |

- Yellow headers for Form columns, white for Qualtrics, as in her template.
- Every money value is a total salary, shown as `$72,000` (a number formatted with `$` and commas, so Excel can still do math on it).
- Names come from her roster, not as typed.
- Three-person matches, absent students, alternate-row shading, and the color legend work as on the Used Car sheet.
- Extra tabs: `Roles`, plus the three exports untouched (`Supervisor survey`, `Subordinate survey`, `Form`).

**Cleaning** reuses the Used Car rules (typos fixed in orange, unclear answers kept as typed in light red, original in a comment), plus:
- **Raise or total:** a number under $40,000 is a raise and gets the base ($60,000) added; $40,000 or more is already a total. The cell comment shows what was typed. Not highlighted, since it isn't a correction. Both numbers are settings, easy to change after the meeting.
- **"No Deal"** and other words in BASE/RAISE/TOTAL are kept as typed.
- **Duplicates:** the latest Qualtrics response and the latest Form row per match are used; the summary lists what was skipped.

**Matching:**
- Qualtrics responses are matched to students as in Used Car (names, email, nicknames; anything unclear is asked).
- A Form row is matched to a match by its match number, checked against the names typed. If the number is wrong (`66000`, `7 + Siobhan O'Neill`) but the names point to one match, the names win and the summary says so. Otherwise she's asked.
- The two Qualtrics files are told apart by their questions (Supervisor vs. Subordinate), so she doesn't need to say which is which.

**Also:** fictional example files in her exact formats (two Qualtrics exports, a Form CSV with the same kinds of problems as S25, a roster with an `SL` tab), tests, skill instructions, and a Salary step in the Demo Kit.

## Phase 2: Gender and Consent from the Baseline Survey (`negotiation-pairing`)

- New command: she points Claude at the Week 1 baseline export (number codes). Claude reads it once and writes `Gender` and `Consent` in two new columns just after `Email` on the class list tab.
- Values:
  - Gender: `M`, `F`, `Other`.
  - Consent: `Yes`, `No`, or `No (no survey)` for a student who didn't take it.
  - A student who chose "Other" for gender gets `Excluded` in Consent.
- Responses are matched to students by name, as in the other surveys; anything unclear is asked.
- **Risk:** inserting columns moves her attendance dates one column to the right. If that tab has formulas or merged cells to the right of Email, Claude stops and asks her to insert the two blank columns herself, then fills them. Before writing, a backup is made and the shift is checked cell by cell.

## Phase 3: Experimental Conditions for Used Car (`negotiation-pairing`)

Assumption-heavy; to be confirmed in the meeting before relying on it.

1. Students who declined consent (or are excluded) are paired with each other first; their roles may be swapped to make that work.
2. Everyone else: within each gender, alphabetically, the first half is I and the second half C.
3. Within each condition, her usual method: first half Buyers, second half Sellers. Matches stay within one condition.
4. I/C is written in the `Intervention` column of the UC tab.
5. Four BCC lists: Buyer-I, Buyer-C, Seller-I, Seller-C.
6. Absences: a stranded student joins the nearest earlier match in the same condition, or she is asked.

## Not Changing

- Used Car's in-class columns stay hers to fill by hand; Used Car doesn't use the Google Form.
- No email is sent, and her workbook is only written with a backup and a log entry.
- The full research dataset from the codebook, and Prolific, are later.
