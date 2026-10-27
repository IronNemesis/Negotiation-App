# Build Salary Outcomes Sheet Task Specification

## Basic Information

- **Task ID:** T11
- **Task name:** Build Salary Outcomes Sheet
- **Task type:** Act
- **Task owner:** Negotiation Pairing Solution (`bargaining-range-sheet` skill); the Instructor is accountable.

## 1. Task Description

After the Salary negotiation, the Instructor debriefs the outcomes. Until now, students filled in a Google Form in class and she built the outcomes sheet by hand for the next class. Because Claude can build it in about a minute, she wants it in the same class (Meeting 4).

T11 combines three files into her outcomes sheet layout:
- **Two Qualtrics exports** from before class (Supervisor and Subordinate), with each student's planned initial offer, target and reservation. These are cleaned and matched to students with the same rules as T6 and T7.
- **The in-class Google Form CSV**, one row per match: actual initial offers, base, raise, total, threat, minutes, approaches, other terms.

The matches come from the roster's `SL` tab: the final table if absences are in, otherwise the draft.

The details:
- **Total salary:** every money value is shown as a total salary, formatted with `$` and commas. A number under $40,000 is read as a raise on a $60,000 base. Both numbers are settings, and both are still to be confirmed with her.
- **Form rows:** each row is placed on a match by the names typed when they agree on one match, otherwise by the match number. Duplicates use the latest submission. Anything else is her decision (H4).
- **What's flagged:** a total that doesn't equal base + raise, and totals outside the usual range, are highlighted for her to look at. Nothing is changed silently.
- **Missing rows:** students without a survey response, and matches without a Form row, keep their rows with a comment.
- **Absent students:** listed in a block below the matches, as on the Used Car sheet.

## 2. Inputs

- **Supervisor and Subordinate Qualtrics exports** (CSV, number codes, three header rows). Source: the Instructor.
- **Form responses** (CSV downloaded from the Form's Google Sheet). Source: the Instructor, in class.
- **Matches and class list:** the roster's `SL` tab and attendance tab. Source: `negotiation-pairing`.
- **Week number:** for the file name. Source: the Instructor.
- **If a required input is missing or invalid:** without both exports the sheet isn't built (`export_missing`). A Form whose headers changed stops the run (`survey_layout`, H1). Without a Form, the yellow columns are left blank.

## 3. Outputs

- **Salary outcomes workbook:** `<course and term> Week <N> - Salary Negotiation Outcomes.xlsx`, next to the Form CSV, with the sheet, `Roles`, and the three exports untouched. Complete when every student in the matches appears once, every value reads back as written, and every converted, corrected or flagged value has its comment.
- **Build summary:** in the chat and the log. It covers counts, students without a response, matches without a Form row, the Form notes (wrong match numbers, duplicates), flagged cells, and the assumptions used.

## 4. Planned Tools

- **Tool:** `brs.py build --simulation SL` (code in `scripts/salary.py`), a Python script bundled with the skill.
  - Writes into a temporary file and reads every value back before moving it into place.
  - Any earlier version is moved to `Backups` first.
  - It never writes to the roster.
- **Task timeout:** 30 seconds.
- **Retries:** once, if the file is open in Excel. Ask her to close it first.
