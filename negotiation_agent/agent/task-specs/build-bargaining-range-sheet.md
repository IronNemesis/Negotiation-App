# Build Bargaining Range Sheet Task Specification

## Basic Information

- **Task ID:** T8
- **Task name:** Build Bargaining Range Sheet
- **Task type:** Act
- **Task owner:** Negotiation Pairing Solution (`bargaining-range-sheet` skill); the Instructor is accountable.

## 1. Task Description

T8 writes the workbook the Instructor uses for the in-class debrief, in her exact layout (see [`workbook-conventions.md`](../../docs/workbook-conventions.md)). It replaces the cleaning and re-typing she does today.

**Main sheet:**
- One row per match in match order. The Buyer's details fill the left side, `OUTCOME` sits in the middle, and the Seller's details are mirrored on the right, so the two bargaining ranges meet in the middle.
- A second same-role student gets their own row directly under their match, with the match number and the other side left blank.
- Names come from the class list (not as typed in the survey), so they are spelled consistently.
- `ROLE` holds the Qualtrics code (`1` or `2`).
- `ACTUAL IO` (yellow headers) and `OUTCOME` are left blank for her to fill in during class.
- Every other match row is shaded, as in her sheets.
- Highlights from T6 and T7 are applied: orange for corrected typos, light red for unclear answers and role conflicts, with the original answer in a cell comment. A short color legend sits two rows below the table.

**Other tabs:**
- `Roles`: `MATCH | BUYER | SELLER`.
- `Raw`: the untouched export, for reference.

**File name and location:**
- The file is saved next to the Qualtrics export, named `<course and term> Week <N> - Used Car Bargaining Range.xlsx`.
- The course and term come from the roster workbook's name (for example `BUS 4489 F26`).
- Claude asks for the week number, suggesting one if it can tell from the date.

T8 runs twice per simulation: before class from the draft matches, and after the absence update from the final matches. On the second run, the previous file is moved to `Backups` first. If that file already has anything typed in `ACTUAL IO` or `OUTCOME`, T8 stops and asks her before replacing it, because she may have started filling it in.

## 2. Inputs

### Input 1

- **Input name:** Matched responses
- **Contents and format:** From T7, including highlights and comments.
- **Source:** T7: Match Survey Responses to Students.

### Input 2

- **Input name:** Sheet settings
- **Contents and format:** Column order, header text (including the six perception-item headers), role codes, and fill colors for the simulation.
- **Source:** The skill's settings file.

### Input 3

- **Input name:** Week number
- **Contents and format:** The week of the term, for the file name.
- **Source:** The Instructor, in the chat (asked once per simulation).

- **If a required input is missing or invalid:** If the week number isn't given, T8 asks. If a file with the target name is open in Excel, T8 asks her to close it.

## 3. Outputs

### Output 1

- **Output name:** Bargaining range workbook
- **Contents and format:** `<course and term> Week <N> - Used Car Bargaining Range.xlsx` with the main sheet, `Roles`, and `Raw`.
- **Next task or recipient:** The Instructor, for the in-class debrief.
- **Complete when:** Every student in the current matches appears exactly once, in their match's row or the row under it. Every number on the sheet equals its cleaned value from T6 on read-back. Every corrected or unclear value is highlighted and has its comment. `ACTUAL IO` and `OUTCOME` are empty.

### Output 2

- **Output name:** Build summary
- **Contents and format:** Chat summary and log entry: matches, students with no response, corrected and unclear answers, role conflicts, absent students left off, and any previous file moved to `Backups`.
- **Next task or recipient:** The Instructor.
- **Complete when:** The summary is shown and logged.

## 4. Planned Tools

### Tool 1

- **Tool name:** `build_sheet`
- **Input:** Matched responses; Sheet settings; Week number.
- **Output:** Bargaining range workbook; Build summary.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that writes the workbook into a temporary file, reads it back to compare every value, and only then moves it into place.
- **Integration approach:** Direct integration.
- **Role in this task:** Builds the debrief workbook. It never fills `ACTUAL IO` or `OUTCOME`, and never writes to the roster workbook.
- **Task timeout:** 60 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The target file is locked because it is open in Excel. Ask her to close it, then retry once. The workbook is rebuilt in full each time, so a retry cannot duplicate rows.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," keep the temporary file out of her folder, log the error, and tell the Instructor. If the read-back finds a mismatch, the workbook is not presented as finished and the mismatched cells are listed.
