# Resolve Survey Matches Task Specification

## Basic Information

- **Task ID:** H4
- **Task name:** Resolve Survey Matches
- **Task type:** Decide
- **Task owner:** Instructor.

## 1. Task Description

When T7 can't tell with confidence whose response a survey row is, the Instructor decides. Common cases:
- a name that fits no student or more than one;
- a nickname Claude doesn't know;
- a personal email with a name that doesn't match;
- two responses from the same student.

Claude shows every unresolved response in a single message, so she can answer them at once. Each shows the name and email as typed, the submission time, the reason it is unresolved, and up to three suggested students. For duplicates, the usual answer ("use the latest") is offered as a one-word default.

This is her decision because the wrong numbers in the debrief would mislead the class.

## 2. Inputs

### Input 1

- **Input name:** Unresolved responses
- **Contents and format:** From T7.
- **Source:** T7: Match Survey Responses to Students.

### Input 2

- **Input name:** Match decisions
- **Contents and format:** Her reply: for each response, the student it belongs to or "leave out"; for duplicates, which submission to use (or "latest" for all).
- **Source:** Instructor.

- **If a required input is missing or invalid:** A decision giving a response to a student who already has one is shown back to her as a conflict. Responses she doesn't answer stay unresolved, and T8 doesn't run until all are decided.

## 3. Outputs

### Output 1

- **Output name:** Match decisions
- **Contents and format:** Her decision for each unresolved response, recorded in the log.
- **Next task or recipient:** T7, which applies them and passes complete matched responses to T8.
- **Complete when:** Every unresolved response has a recorded decision.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_match_decisions`
- **Input:** Unresolved responses; Match decisions.
- **Output:** Match decisions.
- **Implementation Route:** The chat conversation in the Claude desktop app, plus the shared script's log function.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the unresolved responses and records her answers. It doesn't choose for her.
- **Task timeout:** No fixed deadline; the run waits for the Instructor. The survey closes a few hours before class, so this normally happens well before then.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she ends the session without deciding, no sheet is built, and the log shows "Waiting on Instructor: survey matches."
