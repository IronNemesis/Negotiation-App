# Write Draft Matches Task Specification

## Basic Information

- **Task ID:** T4
- **Task name:** Write Draft Matches
- **Task type:** Remember
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

After the Instructor approves the draft, T4 writes it into the draft table (`MATCH | BUYER | SELLER`) at the bottom of the simulation tab she prepared.

- Names go into the rows she prefilled with match numbers, as `Last, First`, exactly as on the class list.
- A second same-role student goes on the next row, with the match number and the other role left blank.
- Prefilled match rows that aren't needed are left as they are.

T4 writes only to the draft table. The final table at the top is written later by T9, at the absence step (assumption; see open questions). No other tab and no cell outside the draft table is changed.

Before writing, T4 saves a dated copy of the workbook in the `Backups` folder, so any write can be undone by restoring that copy.

## 2. Inputs

### Input 1

- **Input name:** Approved draft matches
- **Contents and format:** Draft matches that passed T3, with the Instructor's approval recorded in H2.
- **Source:** H2: Review Draft Matches.

### Input 2

- **Input name:** Simulation tab layout
- **Contents and format:** Position of the draft table and its prefilled match rows.
- **Source:** T1: Read Class List and Simulation Tab, re-read at the moment of writing.

- **If a required input is missing or invalid:** If no approval is recorded, T4 does not run. If the draft table already contains names, T4 shows the Instructor what is there and asks before replacing it. If the draft needs more rows than she prefilled, T4 stops and asks her to extend the tab rather than writing below it.

## 3. Outputs

### Output 1

- **Output name:** Updated simulation tab
- **Contents and format:** The roster workbook with the draft table filled in, plus a backup named `<workbook name> <date> <time> before <code> draft.xlsx` in `Backups`.
- **Next task or recipient:** T5: Build Role BCC Lists; T7 later reads the draft from here.
- **Complete when:** The backup exists, and reading the saved workbook back shows exactly the approved draft in the draft table, with every other tab and cell unchanged.

### Output 2

- **Output name:** Write entry
- **Contents and format:** Log entry: run ID, simulation, number of matches, backup name, and time.
- **Next task or recipient:** The Instructor, through the log and a one-line summary in the chat.
- **Complete when:** The entry is saved.

## 4. Planned Tools

### Tool 1

- **Tool name:** `write_draft`
- **Input:** Approved draft matches; Simulation tab layout.
- **Output:** Updated simulation tab; Write entry.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that backs up the workbook, writes only the draft-table cells, saves, and compares a read-back against the approved draft and against the backup for every other cell.
- **Integration approach:** Direct integration.
- **Role in this task:** Writes the approved draft. It cannot write anywhere else in the workbook.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The workbook is locked because it is open in Excel. Ask her to close it, then retry once. Before retrying, read the draft table back; if it already matches, do not write again.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Write failed." If the saved file doesn't match, restore the backup. Log what happened and tell the Instructor. T5 does not run until the write is confirmed.
