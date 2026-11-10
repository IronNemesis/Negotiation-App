# Build Process Points Sheet Task Specification

## Basic Information

- **Task ID:** T13
- **Task name:** Build Process Points Sheet
- **Task type:** Act
- **Task owner:** Negotiation Pairing Solution (`bargaining-range-sheet` skill); the Instructor is accountable.

## 1. Task Description

After the Equity Splits negotiation (three cofounders: Michael, Phuc, Georg), each student rates each teammate in a Google Form on five process measures, 0–5: Trust, Respect, Fairness, Interests, Future. The Instructor wants the finished process points sheet during the same class (Meeting 5).

T13 reads the Form CSV and the roster's `ES` tab (the final table if absences are in, otherwise the draft), links every rating to an observer and a teammate, and writes her Week 4 layout:
- one row per rating, sorted by trio, with a `TOTAL` formula;
- names and roles from the roster, with corrections highlighted and what was typed kept in a comment;
- a `By Student` tab with ratings given and received, and yellow for students who haven't rated every teammate (where she wants the yellow is still to be confirmed);
- the Form export untouched on `Raw`.

The Equity Splits tangible-outcomes sheet is not part of this task; its layout is still to come from her.

## 2. Inputs

- **Form responses** (CSV downloaded from the Form's Google Sheet). Source: the Instructor, in class.
- **Teams and class list:** the roster's `ES` tab and attendance tab. Source: `negotiation-pairing`.
- **Week number:** for the file name. Source: the Instructor.
- **If a required input is missing or invalid:** a Form whose headers changed stops the run (`survey_layout`, H1). An `ES` tab with no teams stops it (`no_matches`).

## 3. Outputs

- **Process points workbook:** `<course and term> Week <N> - Equity Splits Process Points.xlsx`, next to the Form CSV. Complete when every rating used appears once, values read back as written, and every correction has its comment.
- **Build summary:** in the chat and the log: ratings used of those expected, corrections, scores kept as typed, duplicates, and who hasn't rated every teammate.

## 4. Planned Tools

- `scripts/brs.py prepare|build|missing --simulation ES --form …` (`process_points.py`).

## 5. Human Decisions (H4)

- A submitter whose name matches no student (`--observer ROW=Last, First`).
- A rating of someone outside the submitter's trio, or of themselves (`--partner ROW=Last, First`, or `--form-skip ROW`).
