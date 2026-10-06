# Resolve Survey Response Exceptions Task Specification

## Basic Information

- **Task ID:** H6
- **Task name:** Resolve Survey Response Exceptions
- **Task type:** Decide
- **Task owner:** Instructor.

## 1. Task Description

When T8 finds survey responses it cannot match one-to-one, the Instructor decides what to do with them. For a student who submitted more than once, the agent shows every submission side by side with times and values; she picks which one to use. Using the most recent submission is offered as a one-word default, so the decision stays quick. For a response whose student ID matches nobody in the pairing, the agent shows the ID entered and the closest paired student IDs; she says which student it belongs to or leaves it out. This is her decision because using the wrong numbers would put incorrect data in front of the class during the debrief. Because Stage 2 should take under 10 minutes, the agent presents all exceptions in a single message so she can answer them at once.

## 2. Inputs

### Input 1

- **Input name:** Survey exception list
- **Contents and format:** Each duplicate (all submissions with times and values) and each unknown response (ID entered, values, and suggested paired students).
- **Source:** T8: Match Survey Responses to Students.

### Input 2

- **Input name:** Exception decisions
- **Contents and format:** The Instructor's reply in the chat: for each duplicate, which submission to use (or "latest" for all); for each unknown response, the student it belongs to or "leave out."
- **Source:** Instructor.

- **If a required input is missing or invalid:** A decision assigning a response to a student who already has a matched response is shown back to her as a conflict. Exceptions she does not answer stay open, and T9 does not run until all have a decision.

## 3. Outputs

### Output 1

- **Output name:** Exception decisions
- **Contents and format:** For each exception: the decision and a Run Log entry recording it.
- **Next task or recipient:** T8: Match Survey Responses to Students, which applies the decisions and completes the matched data for T9.
- **Complete when:** Every exception has a recorded decision.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_survey_exception_decisions`
- **Input:** Survey exception list; Exception decisions.
- **Output:** Exception decisions.
- **Implementation Route:** The agent's chat conversation with the Instructor in the Claude desktop app, plus a local script that writes her decisions to the Run Log.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the exceptions and records her answers. It does not choose between duplicates or assign unknown responses itself.
- **Task timeout:** No fixed deadline; the run waits for the Instructor. Stage 2's 10-minute target assumes she answers within a few minutes.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If the Instructor ends the session without deciding, the Run Log shows the run as "Waiting on Instructor: survey exceptions," and no outcomes workbook is produced.
