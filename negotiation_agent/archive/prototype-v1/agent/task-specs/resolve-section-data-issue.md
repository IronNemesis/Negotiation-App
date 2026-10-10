# Resolve Section Data Issue Task Specification

## Basic Information

- **Task ID:** H1
- **Task name:** Resolve Section Data Issue
- **Task type:** Verify
- **Task owner:** Instructor.

## 1. Task Description

When T1 or T7 cannot read a required file, or finds that a file is not in the expected shape, the Instructor fixes the cause. Common causes include a roster saved under a different name, a renamed column, duplicate student IDs in the roster, a pair ID typed in an unfamiliar format, a survey question renamed in Qualtrics so the column mapping no longer matches, or a missing outcomes template. Fixing these needs her knowledge of her own files and courses, which the agent does not have. The agent explains in plain language exactly which file, sheet, column, or row is the problem, and can suggest a fix, but it does not edit her source files to make the problem go away. H1 exists so the workflow never pairs students or builds a workbook from missing or broken data.

## 2. Inputs

### Input 1

- **Input name:** Retrieval failure report
- **Contents and format:** Run Log entry: run ID, the file, sheet, column, or row that failed, failure category, attempts, and time.
- **Source:** T1: Retrieve Section Roster and Pairing History, or T7: Retrieve Survey Export and Approved Pairs.

### Input 2

- **Input name:** Resolution response
- **Contents and format:** The Instructor's reply in the chat: what was wrong, what she changed, and whether to retry now.
- **Source:** Instructor.

- **If a required input is missing or invalid:** If the failure report is unclear, the agent opens the named file read-only and describes what it sees. A reply that the issue is fixed without a change to the file is accepted, but the retry must succeed before the run continues.

## 3. Outputs

### Output 1

- **Output name:** Resolution record
- **Contents and format:** Run Log entry: run ID, cause, change made, and whether a retry was requested.
- **Next task or recipient:** T1 or T7, whichever failed, when the Instructor asks to retry.
- **Complete when:** The Instructor has described the fix and the retried task reads the data successfully. If the retry fails again, a new failure report is produced and H1 starts again.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_issue_resolution`
- **Input:** Retrieval failure report; Resolution response.
- **Output:** Resolution record.
- **Implementation Route:** The agent's chat conversation with the Instructor in the Claude desktop app, plus a local script that writes the Run Log entry and re-runs the failed retrieval task on request.
- **Integration approach:** Direct integration.
- **Role in this task:** Explains the problem, records her resolution, and retries when asked. It does not edit the roster, Pairing History, survey export, or Simulation Settings.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If the Instructor ends the session without resolving the issue, the Run Log shows the run as "Waiting on Instructor: data issue," and nothing is produced. She can resume later or start a new run.
