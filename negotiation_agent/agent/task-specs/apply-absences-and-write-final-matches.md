# Apply Absences and Write Final Matches Task Specification

## Basic Information

- **Task ID:** T9
- **Task name:** Apply Absences and Write Final Matches
- **Task type:** Remember
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

At the start of class, the Instructor knows who is absent. T9 turns the draft into the final matches using her own rule, so it is a quick update rather than a redo, and roles never change, because every student already has their role packet.

Starting from the draft table as it currently stands in the tab (including any edits she made):

1. Each absent student is removed from their match and recorded as absent, with ID `<code>_0` (for example `UC_0`).
2. If a match still has at least one Buyer and one Seller, nothing else changes.
3. If a match loses its only student in a role, its remaining students are stranded. Each stranded student joins the **match just before theirs** (the nearest lower match number still in use) as an extra student in the same role. If there is no earlier match, they join the next one. The dissolved match number simply disappears; nothing is renumbered.
4. If joining that match would give it more than three students, or would create a repeat partner from an earlier simulation, T9 doesn't choose: it asks the Instructor where the student should go (part of H6).

The proposed final matches are checked by T3, including the rule that no student's role differs from the draft, and shown to her for confirmation (H6).

After she confirms, T9 writes the final table at the top of the simulation tab:
- One row per match: match number in column A; Buyer name, email, and pair ID; Seller name, email, and pair ID (`<code>_<match>`).
- Extra same-role students go on the row under their match, with column A and the other role blank.
- Absent students are listed two rows below the table, with name, email, and `<code>_0`.
- Prefilled match numbers in column A that the final table doesn't use are cleared, but only cells that contain nothing but a number, and only above the draft table.
- `Gender` and `Intervention` are left untouched.

Before writing, T9 backs up the workbook. If nobody is absent, the final table is the draft as it stands.

## 2. Inputs

### Input 1

- **Input name:** Absent students
- **Contents and format:** The students the Instructor reports as absent, matched to the class list (unmatched or ambiguous names are asked about).
- **Source:** H5: Report Absences.

### Input 2

- **Input name:** Current draft and tab layout
- **Contents and format:** The draft table as it stands in the simulation tab, and the position of the final table.
- **Source:** T1: Read Class List and Simulation Tab, re-read for this run.

### Input 3

- **Input name:** Confirmation and placements
- **Contents and format:** Her confirmation of the proposed final matches, and her choice for any student T9 could not place.
- **Source:** H6: Confirm Final Matches.

- **If a required input is missing or invalid:** If the draft table is empty, T9 stops (Stage 1 hasn't been done). If the final table already has names, or the final-table area has anything in `Gender`, `Intervention`, or other cells besides prefilled match numbers, T9 shows her what is there and asks before writing, because rows may shift.

## 3. Outputs

### Output 1

- **Output name:** Proposed final matches
- **Contents and format:** The final matches with every move explained (for example, "Ava Quinn joins match 3 as a second Seller because Jo Evans (match 4) is absent"), plus T3's check report.
- **Next task or recipient:** H6: Confirm Final Matches.
- **Complete when:** Every absent student is recorded, every stranded student is placed or listed for her decision, and T3 finds no errors.

### Output 2

- **Output name:** Updated simulation tab
- **Contents and format:** The roster workbook with the final table written, plus a backup named `<workbook name> <date> <time> before <code> final.xlsx` in `Backups`.
- **Next task or recipient:** The Instructor; T7 then reads the final matches when she re-runs the bargaining range sheet.
- **Complete when:** The backup exists, and the read-back shows exactly the confirmed final table, with every other tab and cell unchanged.

## 4. Planned Tools

### Tool 1

- **Tool name:** `apply_absences`
- **Input:** Absent students; Current draft and tab layout; Confirmation and placements.
- **Output:** Proposed final matches; Updated simulation tab.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that applies the absence rule, calls the same checks as T3, and, after confirmation, backs up the workbook, writes only the final-table area, and compares a read-back with the backup for every other cell.
- **Integration approach:** Direct integration.
- **Role in this task:** Proposes and, after confirmation, writes the final matches. It cannot change roles or write outside the final-table area.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The workbook is locked because it is open in Excel. Ask her to close it, then retry once. Before retrying, read the final table back; if it already matches, do not write again.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Write failed." If the saved file doesn't match, restore the backup. Log what happened and tell the Instructor.
