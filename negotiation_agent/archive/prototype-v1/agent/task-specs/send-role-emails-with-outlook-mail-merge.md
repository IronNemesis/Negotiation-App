# Send Role Emails with Outlook Mail Merge Task Specification

## Basic Information

- **Task ID:** H5
- **Task name:** Send Role Emails with Outlook Mail Merge
- **Task type:** Act
- **Task owner:** Instructor.

## 1. Task Description

The Instructor sends each student their role using the Word and Outlook mail merge she already uses and likes. She connects her role email document to `Role Mail Merge.xlsx` (Mailings → Select Recipients → Use an Existing List), previews a few emails, and finishes the merge to Outlook. Because the workbook's column names are fixed, she can set up the Word document once and reuse it for every simulation and section. Sending stays with her: the agent has no access to Outlook and never emails students. After sending, she tells the agent, and the agent records it in the Run Log so there is a record of which pairing was emailed and when.

## 2. Inputs

### Input 1

- **Input name:** Role Mail Merge workbook
- **Contents and format:** `Role Mail Merge.xlsx` with one row per paired student and fixed columns: First Name, Last Name, Email, Simulation, Role, Role Information, Survey Link, Status.
- **Source:** T6: Build Role Mail Merge Workbook.

### Input 2

- **Input name:** Role email document
- **Contents and format:** The Instructor's Word mail merge document with merge fields matching the workbook's column names.
- **Source:** Instructor (set up once, reused across simulations).

### Input 3

- **Input name:** Send confirmation
- **Contents and format:** The Instructor's reply in the chat that the merge was sent, and any rows she skipped.
- **Source:** Instructor.

- **If a required input is missing or invalid:** If Word reports a missing merge field, the column names in her document and the workbook differ; the agent tells her which column names to use. Rows with "Missing email" are listed so she can reach those students another way.

## 3. Outputs

### Output 1

- **Output name:** Role emails sent
- **Contents and format:** One email per student, sent from the Instructor's Outlook, with that student's role information and survey link.
- **Next task or recipient:** Students; after the survey closes, the Instructor starts Stage 2.
- **Complete when:** The Instructor confirms the merge was sent.

### Output 2

- **Output name:** Send record
- **Contents and format:** Run Log entry: run ID, "role emails sent," skipped rows, and time.
- **Next task or recipient:** The Instructor (visible in the Run Log).
- **Complete when:** The entry is saved.

## 4. Planned Tools

### Tool 1

- **Tool name:** Microsoft Word and Outlook mail merge (Instructor-operated)
- **Input:** Role Mail Merge workbook; Role email document.
- **Output:** Role emails sent.
- **Implementation Route:** The Instructor's existing Word mail merge to Outlook on her Windows computer. The agent's only part is a local script that writes the Send record to the Run Log when she confirms.
- **Integration approach:** Manual; no integration with Outlook.
- **Role in this task:** The Instructor performs and controls the send. The agent can explain the mail merge steps if asked.
- **Task timeout:** No fixed deadline; she sends whenever she is ready before class.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she does not confirm the send, the Run Log shows "Role emails not confirmed." The pairing remains recorded, and Stage 2 can still run.
