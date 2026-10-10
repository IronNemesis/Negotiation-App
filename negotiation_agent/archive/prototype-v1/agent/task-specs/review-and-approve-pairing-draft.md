# Review and Approve Pairing Draft Task Specification

## Basic Information

- **Task ID:** H4
- **Task name:** Review and Approve Pairing Draft
- **Task type:** Verify
- **Task owner:** Instructor.

## 1. Task Description

The Instructor reviews `Pairing Draft.xlsx` and its Checks sheet and decides whether to use it. She knows things the system does not, such as two students who should be kept apart or a student who needs a particular partner. She has four choices:
- **Approve** the draft as it is.
- **Edit** the draft directly in Excel (swap partners, change roles), save it, and tell the agent to re-check it. T4 then validates her version and shows her any new warnings.
- **Request a new draft**, optionally with constraints such as "keep these two apart," which sends the case back to T3.
- **Cancel** the run.

A draft with errors (a missing or duplicated student, an absent student, a pair without both roles) cannot be approved until they are fixed. Warnings, such as a repeat partner or a role imbalance, can be approved if she confirms them. This checkpoint is what keeps her in control: nothing is recorded in her Pairing History and no mail merge file is built until she approves.

## 2. Inputs

### Input 1

- **Input name:** Validated pairing draft
- **Contents and format:** `Pairing Draft.xlsx` with its Checks sheet, and the chat summary of errors and warnings.
- **Source:** T4: Validate Pairing Draft.

### Input 2

- **Input name:** Review decision
- **Contents and format:** The Instructor's reply in the chat: approve, re-check my edits, new draft (with optional constraints), or cancel. Approving a draft with warnings requires her to confirm each warning.
- **Source:** Instructor.

- **If a required input is missing or invalid:** If she approves a draft that still has errors, the agent lists the errors and does not record approval. If she says she edited the draft but the file has not changed since the last check, the agent asks her to save the file and confirm again.

## 3. Outputs

### Output 1

- **Output name:** Approved pairing
- **Contents and format:** Run Log entry: run ID, "approved," any warnings she accepted, and time. The approved `Pairing Draft.xlsx` is kept unchanged as the record of this pairing.
- **Next task or recipient:** T5: Record Pairs in Pairing History.
- **Complete when:** One approval is recorded for a draft with no errors.

### Output 2

- **Output name:** Edit or new draft request
- **Contents and format:** Run Log entry: "re-check edits" (back to T4) or "new draft" with any constraints (back to T3).
- **Next task or recipient:** T4: Validate Pairing Draft, or T3: Generate Unique Pairs and Assign Roles.
- **Complete when:** The request is recorded and the next task has started.

### Output 3

- **Output name:** Cancellation
- **Contents and format:** Run Log entry: run ID, "canceled," and time. The draft file is kept for reference but marked "Not approved" in its file name.
- **Next task or recipient:** None; the run ends with nothing recorded.
- **Complete when:** The cancellation is recorded.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_review_decision`
- **Input:** Validated pairing draft; Review decision.
- **Output:** Approved pairing; Edit or new draft request; Cancellation.
- **Implementation Route:** The agent's chat conversation with the Instructor in the Claude desktop app, plus a local script that checks for errors before recording approval and writes the decision to the Run Log.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the draft, records her decision, and routes the run. It does not approve a draft on her behalf, and it never treats silence as approval.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If the Instructor ends the session without deciding, the draft stays unapproved, the Run Log shows the run as "Waiting on Instructor: pairing review," and nothing is recorded. Only one approval per run ID is applied, so confirming twice cannot record the pairing twice.
