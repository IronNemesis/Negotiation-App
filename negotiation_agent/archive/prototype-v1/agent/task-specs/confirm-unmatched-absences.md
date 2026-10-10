# Confirm Unmatched Absences Task Specification

## Basic Information

- **Task ID:** H2
- **Task name:** Confirm Unmatched Absences
- **Task type:** Decide
- **Task owner:** Instructor.

## 1. Task Description

When an absence the Instructor listed does not match exactly one roster student, she decides who she meant. Examples include a nickname ("Alex" for Alejandro), a misspelling, a first name shared by two students, or someone who has dropped the class. The agent shows each unmatched entry with up to three suggested roster names. She confirms a suggestion, names a different student, or tells the agent to ignore the entry. This decision is hers because a wrong guess either pairs an absent student, leaving a partner without a negotiation, or leaves out a student who is present.

## 2. Inputs

### Input 1

- **Input name:** Unmatched absence list
- **Contents and format:** Each unmatched or ambiguous entry, the reason, and up to three suggested roster names.
- **Source:** T2: Build Attendance List from Absences.

### Input 2

- **Input name:** Absence decisions
- **Contents and format:** The Instructor's reply in the chat for each entry: a suggested name, another roster student, or "ignore."
- **Source:** Instructor.

- **If a required input is missing or invalid:** A reply naming someone who is still not on the roster is shown back to her with new suggestions. An entry she does not answer stays unresolved, and T3 does not run until every entry has a decision.

## 3. Outputs

### Output 1

- **Output name:** Absence decisions
- **Contents and format:** For each entry: the roster student it refers to, or "ignored," plus a Run Log entry recording each decision.
- **Next task or recipient:** T2: Build Attendance List from Absences, which applies the decisions and completes the attendance list.
- **Complete when:** Every unmatched entry has a recorded decision.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_absence_decisions`
- **Input:** Unmatched absence list; Absence decisions.
- **Output:** Absence decisions.
- **Implementation Route:** The agent's chat conversation with the Instructor in the Claude desktop app, plus a local script that writes her decisions to the Run Log.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the entries and suggestions and records her answers. It does not choose a match itself.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If the Instructor ends the session without deciding, the Run Log shows the run as "Waiting on Instructor: absences," and no pairing is produced.
