# Validate Pairing Draft Task Specification

## Basic Information

- **Task ID:** T4
- **Task name:** Validate Pairing Draft
- **Task type:** Verify
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T4 checks a pairing draft against fixed rules and saves it as `Pairing Draft.xlsx` in the simulation folder for the Instructor to review. It runs twice in the normal cycle: once on the draft T3 generates, and again every time the Instructor edits the draft directly in Excel during H4. Checking her edits with the same rules lets her change anything she wants while still seeing the consequences before she approves. T4 reports problems; it never undoes or changes her edits.

The rules are:
1. Every attending student appears exactly once.
2. No absent student and no student outside the roster appears.
3. Every pair has one student in each role, except an approved H3 arrangement.
4. Every pair whose members already share a pair ID is flagged as a repeat.
5. When role balancing is on, any student given a role they have played more often than the other is flagged.

Rules 1–3 are errors that block approval. Rules 4–5 are warnings the Instructor may accept.

## 2. Inputs

### Input 1

- **Input name:** Pairing draft
- **Contents and format:** The draft from T3, or the Instructor's edited `Pairing Draft.xlsx`.
- **Source:** T3: Generate Unique Pairs and Assign Roles, or H4: Review and Approve Pairing Draft.

### Input 2

- **Input name:** Attendance list and pair history
- **Contents and format:** Attending and absent students from T2; pair IDs and past roles from T1.
- **Source:** T1 and T2.

- **If a required input is missing or invalid:** If the edited workbook cannot be read, or its columns have been renamed or removed, T4 reports which column it could not find and asks the Instructor to restore it. It does not guess what an edited cell means.

## 3. Outputs

### Output 1

- **Output name:** Validated pairing draft
- **Contents and format:** `Pairing Draft.xlsx` in the simulation folder: one row per student (pair number, student ID, name, role, partner name), plus a Checks sheet listing every error and warning in plain language and a summary line (for example, "0 errors, 1 warning: Ana Ruiz and Ben Cho negotiated together in Used Car on 2026-10-01").
- **Next task or recipient:** H4: Review and Approve Pairing Draft (Instructor).
- **Complete when:** All five rules have been checked, the Checks sheet lists every finding, and the workbook is saved and summarized in the chat.

## 4. Planned Tools

### Tool 1

- **Tool name:** `validate_pairing`
- **Input:** Pairing draft; Attendance list and pair history.
- **Output:** Validated pairing draft.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that applies the five rules and writes the draft and Checks sheet to `Pairing Draft.xlsx`. On a re-check, only the Checks sheet is rewritten, so the Instructor's edits are kept exactly as she made them.
- **Integration approach:** Direct integration.
- **Role in this task:** Checks and reports. It cannot approve a draft or change pairs or roles.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** `Pairing Draft.xlsx` is locked because it is open in Excel. Ask the Instructor to save and close it, then retry once.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Validation failed," record the error in the Run Log, and tell the Instructor in the chat. A draft that has not passed validation cannot be approved in H4.
