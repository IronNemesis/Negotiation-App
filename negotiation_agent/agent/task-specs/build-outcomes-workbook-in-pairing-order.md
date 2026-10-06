# Build Outcomes Workbook in Pairing Order Task Specification

## Basic Information

- **Task ID:** T9
- **Task name:** Build Outcomes Workbook in Pairing Order
- **Task type:** Act
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T9 produces the outcomes workbook the Instructor uses in class, replacing the manual re-entry of survey data. It starts from a copy of the simulation's outcomes template, so the layout, formulas, and formatting are hers. It fills in one row per student, ordered by pair, with partners on adjacent rows (assumed until confirmed; see `docs/open-questions.md`). Each student's survey numbers are copied exactly, with no rounding or reformatting. The outcome column stays blank for her to fill in during class. Students marked "No response" keep their row with the survey cells empty and a note, so the pair is still visible. Before handing the workbook over, T9 reads it back and compares every copied number with the survey export, because one mistyped number would undermine the debrief. The whole of Stage 2 should finish within 10 minutes.

## 2. Inputs

### Input 1

- **Input name:** Matched survey data
- **Contents and format:** One record per paired student with pair number, role, bargaining values, and match status.
- **Source:** T8: Match Survey Responses to Students.

### Input 2

- **Input name:** Outcomes template
- **Contents and format:** The simulation's template workbook in the Templates folder, with its column headers matching the outcomes columns named in the survey column mapping.
- **Source:** The Instructor, who maintains the template.

- **If a required input is missing or invalid:** If a mapped outcomes column does not exist in the template, T9 stops before writing and tells the Instructor which column is missing. If an `Outcomes.xlsx` already exists in the simulation folder, T9 does not overwrite it; it moves the old file to Backups first, because she may have already entered outcomes in it.

## 3. Outputs

### Output 1

- **Output name:** Outcomes workbook
- **Contents and format:** `Outcomes.xlsx` in the simulation folder: a copy of the template with one row per paired student in pair order, the pair number, name, role, and survey values filled in, notes for "No response" students, and an empty outcome column.
- **Next task or recipient:** The Instructor, who fills in the outcome column during class.
- **Complete when:** Every paired student appears exactly once, partners are on adjacent rows, every copied survey value matches the export exactly on read-back, the outcome column is empty, and the chat summary states the counts of matched and "No response" students.

### Output 2

- **Output name:** Completion entry
- **Contents and format:** Run Log entry: run ID, workbook name, counts, any backup made, and total Stage 2 time.
- **Next task or recipient:** The Instructor (visible in the Run Log).
- **Complete when:** The entry is saved.

## 4. Planned Tools

### Tool 1

- **Tool name:** `build_outcomes_workbook`
- **Input:** Matched survey data; Outcomes template.
- **Output:** Outcomes workbook; Completion entry.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that copies the template, writes values only into the mapped cells (leaving her formulas and formatting untouched), saves, and compares a read-back against the survey export.
- **Integration approach:** Direct integration.
- **Role in this task:** Builds the workbook from the template. It cannot fill in outcomes, and it cannot overwrite an existing outcomes file without first backing it up.
- **Task timeout:** 60 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The file is locked because it is open in Excel. Ask the Instructor to close it, then retry once. The workbook is rebuilt in full from the template each time, so a retry cannot duplicate rows.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," keep any partial file out of the simulation folder, record the error in the Run Log, and tell the Instructor in the chat. If the read-back finds a mismatch, the workbook is not presented as finished, and the mismatched cells are listed.
