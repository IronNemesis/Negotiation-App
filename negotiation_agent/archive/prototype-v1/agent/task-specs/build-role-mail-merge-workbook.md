# Build Role Mail Merge Workbook Task Specification

## Basic Information

- **Task ID:** T6
- **Task name:** Build Role Mail Merge Workbook
- **Task type:** Act
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T6 prepares the data source for the Instructor's Outlook mail merge so she can email every student their role with one merge. It creates `Role Mail Merge.xlsx` with one row per paired student and a fixed set of column headers. The column names never change between runs, so her Word mail merge document keeps working for every simulation and section. Role information comes from Simulation Settings, either as text inserted into the email body or as a link to the role document. Outlook mail merge cannot attach a different file to each email. T6 does not send anything; sending stays with the Instructor in H5. By default, rows do not include the partner's name, because whether students learn their partner by email or in class is still to be confirmed (see `docs/open-questions.md`).

## 2. Inputs

### Input 1

- **Input name:** Approved pairing
- **Contents and format:** Student ID, name, and role for every paired student, confirmed as recorded by T5.
- **Source:** T5: Record Pairs in Pairing History.

### Input 2

- **Input name:** Student contact details
- **Contents and format:** First name, last name, and email address from the section snapshot.
- **Source:** T1: Retrieve Section Roster and Pairing History.

### Input 3

- **Input name:** Simulation configuration
- **Contents and format:** Simulation name, role information text or link for each role, and survey link.
- **Source:** T1: Retrieve Section Roster and Pairing History.

- **If a required input is missing or invalid:** A student with no email address is kept in the workbook with "Missing email" in the Status column and listed in the chat, so the Instructor can contact them separately; the merge skips that row only if she filters it out. If a role has no role information in Simulation Settings, T6 stops and asks the Instructor to add it, rather than producing emails without role details.

## 3. Outputs

### Output 1

- **Output name:** Role Mail Merge workbook
- **Contents and format:** `Role Mail Merge.xlsx` in the simulation folder, one row per paired student, with columns: First Name, Last Name, Email, Simulation, Role, Role Information, Survey Link, Status.
- **Next task or recipient:** H5: Send Role Emails with Outlook Mail Merge (Instructor).
- **Complete when:** Every paired student has exactly one row, every role value matches the approved pairing, every row with an email has role information, and the column headers match the fixed list.

## 4. Planned Tools

### Tool 1

- **Tool name:** `build_mail_merge_sheet`
- **Input:** Approved pairing; Student contact details; Simulation configuration.
- **Output:** Role Mail Merge workbook.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that writes the workbook with fixed headers and reads it back to compare roles against the approved pairing.
- **Integration approach:** Direct integration.
- **Role in this task:** Prepares the mail merge data. It cannot send email and has no access to Outlook.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** The workbook is locked because it is open in Excel. Ask the Instructor to close it, then retry once. The file is rebuilt in full each time, so a retry cannot create duplicate rows.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," record the error in the Run Log, and tell the Instructor in the chat. The pairing remains recorded; she can ask for T6 to run again without repeating Stage 1.
