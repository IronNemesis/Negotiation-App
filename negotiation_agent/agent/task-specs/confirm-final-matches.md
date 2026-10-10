# Confirm Final Matches Task Specification

## Basic Information

- **Task ID:** H6
- **Task name:** Confirm Final Matches
- **Task type:** Verify
- **Task owner:** Instructor.

## 1. Task Description

Before the final table is written, the Instructor sees the proposed final matches. Every move is explained in one line (for example, "Ava Quinn joins match 3 as a second Seller because Jo Evans is absent"), together with T3's findings.

She can:
- **confirm**;
- **change a placement** (for example, put the stranded student in a different match);
- **choose where a student goes** when T9 couldn't place them, because the match was full or would repeat a partner.

Roles can't change at this point, because packets were sent. Claude explains that if she asks.

This happens in class, so Claude keeps the proposal to a short table plus the moves, and asks one question at a time only when T9 needs a decision.

## 2. Inputs

### Input 1

- **Input name:** Proposed final matches
- **Contents and format:** From T9, with the explained moves and T3's check report.
- **Source:** T9: Apply Absences and Write Final Matches.

### Input 2

- **Input name:** Confirmation or changes
- **Contents and format:** Her reply: confirm, or a placement change.
- **Source:** Instructor.

- **If a required input is missing or invalid:** A placement change that would leave a match without one of each role, or put more than three students in a match, is shown back to her with T3's finding before anything is written.

## 3. Outputs

### Output 1

- **Output name:** Confirmed final matches
- **Contents and format:** Log entry: run ID, "final matches confirmed," any placement changes, and time.
- **Next task or recipient:** T9, which writes the final table; then she re-runs the bargaining range sheet.
- **Complete when:** One clear confirmation is recorded for matches with no errors.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_final_confirmation`
- **Input:** Proposed final matches; Confirmation or changes.
- **Output:** Confirmed final matches.
- **Implementation Route:** The chat conversation in the Claude desktop app, plus the shared script's log function.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the proposal and records her decision. It never treats silence as confirmation.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she ends the session without confirming, the final table is not written, and the log shows "Waiting on Instructor: final matches."
