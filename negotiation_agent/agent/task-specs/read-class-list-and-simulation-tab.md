# Read Class List and Simulation Tab Task Specification

## Basic Information

- **Task ID:** T1
- **Task name:** Read Class List and Simulation Tab
- **Task type:** Retrieve
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

T1 starts every pairing run, both the draft (Stage 1) and the absence update (Stage 3). It reads everything the later tasks need from the Instructor's roster workbook and changes nothing.

It reads:
- the class list from the attendance tab;
- the simulation tab she prepared for this simulation (for example `UC`), locating its final table and draft table by their header rows;
- every pair ID on every earlier simulation tab, so repeat partners can be detected.

Students are identified by name (`Last, First`) and Cal Poly email, as in her workbook. T1 applies fixed rules: a name on a simulation tab is linked to a class-list student when the name matches after ignoring case and extra spaces, or when the email matches. Anything that cannot be linked is reported, not guessed.

## 2. Inputs

### Input 1

- **Input name:** Roster workbook
- **Contents and format:** The Instructor's course workbook (for example `BUS 4489 F26 Roster.xlsx`). The attendance tab (`Att - Fall` or `Att - Spring`) has `Student Name` (`Last, First`) and `Email` columns. Simulation tabs are named with two-letter codes and follow [`workbook-conventions.md`](../../docs/workbook-conventions.md).
- **Source:** The Instructor's own file, in the folder she gives Claude access to.

### Input 2

- **Input name:** Simulation settings
- **Contents and format:** The skill's settings entry for the simulation: code (`UC`), name (Used Car), role names (`BUYER`, `SELLER`), Qualtrics role codes (`1`, `2`).
- **Source:** The skill's own settings file, maintained by the system designer.

### Input 3

- **Input name:** Run request
- **Contents and format:** The Instructor's chat request: simulation, stage (draft or absences), and any students she already knows are absent.
- **Source:** The Instructor, in the Claude desktop app.

- **If a required input is missing or invalid:** If the workbook cannot be opened, the attendance tab or the simulation tab is missing, or the simulation tab has no recognizable header row for the final or draft table, T1 stops with status "Retrieval failed" and the case goes to H1: Resolve Workbook or Survey Data Issue. A class-list row without a name is skipped and reported; a row without an email is kept but reported, because BCC lists and survey matching need it.

## 3. Outputs

### Output 1

- **Output name:** Class snapshot
- **Contents and format:** Structured record: run ID, workbook path, simulation code, class list (name, email), students missing an email, and a sorted list ready for drafting.
- **Next task or recipient:** T2: Draft Matches, T5: Build Role BCC Lists, T9: Apply Absences and Write Final Matches.
- **Complete when:** Every class-list row has been read, and every student has a unique name.

### Output 2

- **Output name:** Simulation tab layout
- **Contents and format:** Structured record: the header row and column positions of the final table and the draft table, the prefilled match numbers, the current contents of both tables, and the role names in the headers.
- **Next task or recipient:** T4: Write Draft Matches, T9: Apply Absences and Write Final Matches.
- **Complete when:** Both tables are located, and the role names in the headers match the simulation settings.

### Output 3

- **Output name:** Pair history
- **Contents and format:** For each student, every pair ID from every earlier simulation tab (for example `UC_4`, `SL_12`), with `_0` entries kept but marked as absences. Earlier-tab names that don't match the class list are listed separately.
- **Next task or recipient:** T3: Check Matches.
- **Complete when:** Every earlier simulation tab with pair IDs has been read. For Used Car, the first simulation of the term, this record is normally empty.

### Output 4

- **Output name:** Retrieval failure report
- **Contents and format:** Log entry produced only on failure: run ID, the tab, table, or column that failed, failure category, attempts, and time.
- **Next task or recipient:** H1: Resolve Workbook or Survey Data Issue.
- **Complete when:** The report names the exact tab and cell area that failed and is explained in the chat.

## 4. Planned Tools

### Tool 1

- **Tool name:** `read_workbook`
- **Input:** Roster workbook; Simulation settings; Run request.
- **Output:** Class snapshot; Simulation tab layout; Pair history; Retrieval failure report.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill (shared with `bargaining-range-sheet`) that opens the workbook read-only and applies the linking rules. The only write is the log entry.
- **Integration approach:** Direct integration.
- **Role in this task:** Reads and reports. It cannot change the workbook.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The workbook is locked because it is open in Excel or syncing in OneDrive. Ask the Instructor to close it, then retry once.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Retrieval failed," log the failure report, and hand the case to H1. Do not continue with a partial class list or an unread earlier tab, because either could hide a repeat partner.
