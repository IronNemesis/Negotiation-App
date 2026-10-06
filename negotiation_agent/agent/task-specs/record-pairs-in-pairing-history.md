# Record Pairs in Pairing History Task Specification

## Basic Information

- **Task ID:** T5
- **Task name:** Record Pairs in Pairing History
- **Task type:** Remember
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T5 adds the approved pairing to the section's Pairing History workbook, so future pairings avoid these partners. It gives each pair a new pair ID in the Instructor's existing format, continuing from the highest ID already used, and attaches that ID to both students the same way she does today. When the history records roles, T5 records each student's role as well. Students in a group of three share one pair ID; a student who observed or partnered with the Instructor receives no pair ID this round. T5 only adds; it never changes or removes an existing pair ID. Before writing, it saves a dated copy of the workbook in the Backups folder, so any recording can be undone by restoring that copy.

## 2. Inputs

### Input 1

- **Input name:** Approved pairing
- **Contents and format:** The validated `Pairing Draft.xlsx` with the Instructor's approval recorded in H4.
- **Source:** H4: Review and Approve Pairing Draft.

### Input 2

- **Input name:** Pairing History
- **Contents and format:** The section's current `Pairing History.xlsx`, re-read at the moment of writing, and the pair-ID format detected by T1.
- **Source:** The section folder; T1: Retrieve Section Roster and Pairing History.

- **If a required input is missing or invalid:** If no approval is recorded, T5 does not run. If the Pairing History has changed since T1 read it (for example, she edited it by hand in the meantime), T5 re-checks the approved pairs against the new history; if any pair has become a repeat, it stops and returns the case to H4 with the new warning.

## 3. Outputs

### Output 1

- **Output name:** Updated Pairing History
- **Contents and format:** `Pairing History.xlsx` with the new pair ID (and role, if tracked) added for every paired student, plus a backup copy named `Pairing History <date> <time> before <simulation>.xlsx` in Backups.
- **Next task or recipient:** T6: Build Role Mail Merge Workbook; future T1 runs.
- **Complete when:** The backup exists, every paired student has exactly one new ID for this simulation, every new ID is shared by exactly the members of one approved pair or group, and a read-back of the saved workbook matches the approved pairing.

### Output 2

- **Output name:** Recording entry
- **Contents and format:** Run Log entry: run ID, simulation, new pair IDs issued, backup file name, and time.
- **Next task or recipient:** The Instructor (visible in the Run Log and summarized in the chat).
- **Complete when:** The entry is saved.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_pairs`
- **Input:** Approved pairing; Pairing History.
- **Output:** Updated Pairing History; Recording entry.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that copies the workbook to Backups, appends the new IDs in the existing format, saves, and reads the file back to confirm.
- **Integration approach:** Direct integration.
- **Role in this task:** Adds the approved pairs to the history. It cannot edit or delete existing entries, and it records only a pairing approved in H4.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The workbook is locked because it is open in Excel. Ask the Instructor to close it, then retry once. Before retrying, read the workbook back; if this run's IDs are already present, do not write again, so a retry cannot record the pairing twice.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Recording failed," restore the backup if the saved file does not match the approved pairing, record what happened in the Run Log, and tell the Instructor. T6 does not run until the recording is confirmed.
