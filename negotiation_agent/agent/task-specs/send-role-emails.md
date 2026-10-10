# Send Role Emails Task Specification

## Basic Information

- **Task ID:** H3
- **Task name:** Send Role Emails
- **Task type:** Act
- **Task owner:** Instructor.

## 1. Task Description

The Instructor emails each role its role packet the way she does today: one email per role in Outlook, with the packet attached and that role's students pasted from T5's list into BCC. Sending stays entirely with her; Claude has no access to Outlook.

When she tells Claude the emails are sent, Claude records it. From then on, roles for this simulation are locked: the absence update (T9) may move students between matches but never changes a role, and Claude won't apply draft changes that would change one. If she later wants to change a role anyway, Claude reminds her the student already has the other packet and asks her to confirm she will re-send.

## 2. Inputs

### Input 1

- **Input name:** Role BCC lists
- **Contents and format:** One semicolon-separated list per role.
- **Source:** T5: Build Role BCC Lists.

### Input 2

- **Input name:** Role packets
- **Contents and format:** The packet file for each role.
- **Source:** The Instructor's own course files.

### Input 3

- **Input name:** Send confirmation
- **Contents and format:** Her reply in the chat that the role emails were sent.
- **Source:** Instructor.

- **If a required input is missing or invalid:** Students missing an email were named by T5; she contacts them another way.

## 3. Outputs

### Output 1

- **Output name:** Role emails sent
- **Contents and format:** One email per role from her Outlook, with the packet attached and the role's students on BCC.
- **Next task or recipient:** Students.
- **Complete when:** She confirms the emails were sent.

### Output 2

- **Output name:** Roles locked record
- **Contents and format:** Log entry: run ID, "role emails sent, roles locked," and time.
- **Next task or recipient:** T9 and any later draft change, which check it.
- **Complete when:** The entry is saved.

## 4. Planned Tools

### Tool 1

- **Tool name:** Outlook (Instructor-operated)
- **Input:** Role BCC lists; Role packets.
- **Output:** Role emails sent.
- **Implementation Route:** Her usual Outlook emails. The agent's only part is the shared script's log function, which records her confirmation.
- **Integration approach:** Manual; no integration with Outlook.
- **Role in this task:** She performs and controls the send.
- **Task timeout:** No fixed deadline; she sends when ready.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she never confirms, the log shows "Role emails not confirmed," and Claude treats roles as locked anyway once it is class day, asking her before any role change.
