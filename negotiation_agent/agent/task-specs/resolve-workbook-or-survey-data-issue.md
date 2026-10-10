# Resolve Workbook or Survey Data Issue Task Specification

## Basic Information

- **Task ID:** H1
- **Task name:** Resolve Workbook or Survey Data Issue
- **Task type:** Verify
- **Task owner:** Instructor.

## 1. Task Description

When a task cannot read the roster workbook or the survey export, or finds them laid out differently than expected, the Instructor fixes the cause. Common causes:
- the simulation tab hasn't been prepared;
- a header was renamed;
- the class list moved to a differently named tab;
- the prepared tab has fewer match rows than the class needs;
- the Qualtrics survey was edited so a question code changed;
- a file is saved somewhere Claude can't reach.

Fixing these needs her knowledge of her own files. Claude explains exactly which file, tab, and cell area is the problem and suggests a fix, but doesn't rearrange her workbook or edit the export to make the problem go away. If her layout has changed in a way the skill can't handle, Claude says so, and the system designer updates the skill.

## 2. Inputs

### Input 1

- **Input name:** Failure report
- **Contents and format:** Log entry: run ID, the file, tab, or column that failed, failure category, attempts, and time.
- **Source:** T1, T6, or any task that read a file.

### Input 2

- **Input name:** Resolution response
- **Contents and format:** The Instructor's reply in the chat: what was wrong, what she changed, and whether to try again.
- **Source:** Instructor.

- **If a required input is missing or invalid:** If the report is unclear, Claude opens the file read-only and describes what it sees. A reply that the issue is fixed is accepted, but the retried task must succeed before the run continues.

## 3. Outputs

### Output 1

- **Output name:** Resolution record
- **Contents and format:** Log entry: run ID, cause, change made, and whether a retry was requested.
- **Next task or recipient:** The task that failed, when she asks to try again.
- **Complete when:** She has described the fix and the retried task succeeds. If it fails again, a new failure report starts H1 again.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_issue_resolution`
- **Input:** Failure report; Resolution response.
- **Output:** Resolution record.
- **Implementation Route:** The chat conversation in the Claude desktop app, plus the shared script's log function and a re-run of the failed task on request.
- **Integration approach:** Direct integration.
- **Role in this task:** Explains the problem, records her fix, and retries when asked. It does not edit her workbook or the export.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she ends the session without resolving the issue, the log shows "Waiting on Instructor: data issue," and nothing is written.
