# Retrieve Section Roster and Pairing History Task Specification

## Basic Information

- **Task ID:** T1
- **Task name:** Retrieve Section Roster and Pairing History
- **Task type:** Retrieve
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T1 starts every Stage 1 run. It reads the section's roster, the section's Pairing History workbook, and the requested simulation's row in Simulation Settings, then hands a clean snapshot to the rest of the workflow. Pairing is only as good as the history it starts from, so T1 applies fixed rules instead of judgment. A student is pairable when they have a roster row with a student ID, a name, and, when the roster has a status column, a status of "Enrolled." Students with any other status (for example, "Dropped") are excluded from pairing. Their Pairing History rows are still read, so their past partners remain on record, and they are listed as "in history, not enrolled." Duplicate student IDs are not merged automatically; they stop the run, because pairing the wrong record would corrupt the history. Each student's existing pair IDs are read exactly as the Instructor recorded them, and T1 learns the format of her pair IDs (for example, `UC-01` or plain numbers) so T5 can continue it. T1 does not change any file.

## 2. Inputs

### Input 1

- **Input name:** Section roster
- **Contents and format:** `Roster.xlsx` in the section folder: one row per student with student ID, name, email address, and enrollment status. Extra columns are ignored.
- **Source:** The Instructor, who saves the official roster export into the section folder at the start of the term.

### Input 2

- **Input name:** Pairing History
- **Contents and format:** `Pairing History.xlsx` in the section folder: the Instructor's existing spreadsheet, with one row per student and the pair IDs from past negotiations attached to each student's name. Optionally includes the role each student played in each past negotiation.
- **Source:** The Instructor's existing pair-ID spreadsheet, updated by T5 after each approved pairing.

### Input 3

- **Input name:** Simulation settings
- **Contents and format:** The requested simulation's row in `Simulation Settings.xlsx`: simulation name, roles (for example, Buyer and Seller), role information text or link, survey link, survey column mapping, outcomes template file name, and whether role balancing is on.
- **Source:** The Instructor, who maintains Simulation Settings.

### Input 4

- **Input name:** Run request
- **Contents and format:** The Instructor's chat request: section, simulation name, and the list of absent students as she wrote it.
- **Source:** The Instructor, in the Claude desktop app.

- **If a required input is missing or invalid:** If the roster or Pairing History cannot be read, the simulation is not listed in Simulation Settings, the roster contains duplicate student IDs, or the pair-ID format cannot be determined from the Pairing History, T1 stops with status "Retrieval failed" and the case goes to H1: Resolve Section Data Issue. No pairing is produced from missing or ambiguous data. Individual roster rows without a student ID, or with a status other than "Enrolled," do not stop the run; they are excluded from pairing and listed in the snapshot with the reason.

## 3. Outputs

### Output 1

- **Output name:** Section snapshot
- **Contents and format:** Structured record: run ID, section, simulation, retrieval time, pairable student list (student ID, name, email, existing pair IDs, past roles if recorded), excluded roster rows with reasons, and the detected pair-ID format and next available pair ID.
- **Next task or recipient:** T2: Build Attendance List from Absences; the pair history is also used by T3 and T4.
- **Complete when:** Every roster row has been classified as pairable or excluded with a reason, and every Pairing History row has been linked to exactly one roster student or listed as unlinked.

### Output 2

- **Output name:** Simulation configuration
- **Contents and format:** Structured record copied from the simulation's Simulation Settings row.
- **Next task or recipient:** T3: Generate Unique Pairs and Assign Roles; T6: Build Role Mail Merge Workbook.
- **Complete when:** The record includes the simulation name and exactly two roles. Simulations with more than two roles are out of scope until confirmed with the Instructor (see `docs/open-questions.md`).

### Output 3

- **Output name:** Retrieval failure report
- **Contents and format:** Run Log entry produced only on failure: run ID, the file or field that failed, failure category, number of attempts, and time of failure.
- **Next task or recipient:** H1: Resolve Section Data Issue (Instructor).
- **Complete when:** The report names the exact file, sheet, or field that failed, and the failure is explained to the Instructor in the chat.

## 4. Planned Tools

### Tool 1

- **Tool name:** `read_section_files`
- **Input:** Section roster; Pairing History; Simulation settings; Run request.
- **Output:** Section snapshot; Simulation configuration; Retrieval failure report.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that reads the section folder's workbooks read-only and applies the pairable, excluded, and linking rules. The only write is the Run Log entry.
- **Integration approach:** Direct integration.
- **Role in this task:** Reads the section's files and returns the snapshot. It cannot edit the roster, the Pairing History, or Simulation Settings.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** A workbook is locked because it is open in Excel. Ask the Instructor to close it, then retry once. Do not retry a missing file, a missing column, or duplicate student IDs. Reads do not change files, so retries cannot create duplicates.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Retrieval failed," write the Retrieval failure report to the Run Log, and hand the case to H1: Resolve Section Data Issue. Do not pass a partial roster to T2 or treat an unreadable Pairing History as empty, because that would allow repeat partners.
