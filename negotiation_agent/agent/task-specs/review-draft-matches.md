# Review Draft Matches Task Specification

## Basic Information

- **Task ID:** H2
- **Task name:** Review Draft Matches
- **Task type:** Verify
- **Task owner:** Instructor.

## 1. Task Description

The Instructor reviews the drafted matches before anything is written to her workbook. Claude shows the draft as a compact table (match, Buyer, Seller), followed by T3's findings in plain words.

She knows things the agent doesn't, such as two students who shouldn't work together, so she can:
- **approve** the draft;
- **ask for specific changes** in the chat ("swap Ana and Ben", "make Kai a Buyer"), which T2 applies and T3 re-checks;
- **edit the draft table directly in Excel** after it's written, then ask Claude to re-check it (T3 reads it back);
- **cancel**.

The draft can keep changing until she sends the role emails (H3); after that, roles are locked. Errors from T3 must be fixed before approval. Repeat-partner warnings can be approved if she confirms each one.

## 2. Inputs

### Input 1

- **Input name:** Draft and check report
- **Contents and format:** The draft matches and T3's errors and warnings.
- **Source:** T2: Draft Matches and T3: Check Matches.

### Input 2

- **Input name:** Review decision
- **Contents and format:** Her reply: approve, specific changes, "I edited the tab, check it", or cancel. Approving with warnings requires confirming each warning.
- **Source:** Instructor.

- **If a required input is missing or invalid:** If she approves a draft that still has errors, Claude lists the errors and doesn't record approval. An ambiguous reply ("looks fine I think") is answered with a direct question rather than treated as approval.

## 3. Outputs

### Output 1

- **Output name:** Approved draft
- **Contents and format:** Log entry: run ID, "draft approved," accepted warnings, and time.
- **Next task or recipient:** T4: Write Draft Matches.
- **Complete when:** One clear approval is recorded for a draft with no errors.

### Output 2

- **Output name:** Change request or cancellation
- **Contents and format:** Log entry with her requested changes (back to T2), "re-check my edits" (back to T3), or "canceled."
- **Next task or recipient:** T2, T3, or none.
- **Complete when:** The request is recorded and the next task has started, or the run has ended.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_draft_review`
- **Input:** Draft and check report; Review decision.
- **Output:** Approved draft; Change request or cancellation.
- **Implementation Route:** The chat conversation in the Claude desktop app, plus the shared script's log function.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the draft and records her decision. It never treats silence as approval.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she ends the session without deciding, nothing is written, and the log shows "Waiting on Instructor: draft review."
