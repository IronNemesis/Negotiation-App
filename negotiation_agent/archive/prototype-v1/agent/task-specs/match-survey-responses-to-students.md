# Match Survey Responses to Students Task Specification

## Basic Information

- **Task ID:** T8
- **Task name:** Match Survey Responses to Students
- **Task type:** Reason
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T8 connects each survey response to a student in the approved pairing. This replaces the step where the Instructor finds each student's row and re-types their numbers. It matches by student ID, ignoring spaces and leading zeros that Excel or Qualtrics may add or drop. Fixed rules decide the common cases without asking her: a paired student with no response is kept with blank survey values and marked "No response," because the pair still negotiates and still appears in the outcomes workbook. Two cases need her judgment and go to H6: Resolve Survey Response Exceptions. One is a student who submitted more than once. The other is a response whose student ID does not belong to anyone in the pairing (a typo, or a student who was marked absent). T8 never deletes a response or chooses between duplicates on its own.

## 2. Inputs

### Input 1

- **Input name:** Survey snapshot
- **Contents and format:** Response rows with student ID as entered, mapped bargaining values, and submission time.
- **Source:** T7: Retrieve Survey Export and Approved Pairs.

### Input 2

- **Input name:** Pairing and template record
- **Contents and format:** The approved pairs with student IDs and roles.
- **Source:** T7: Retrieve Survey Export and Approved Pairs.

### Input 3

- **Input name:** Exception decisions
- **Contents and format:** For each duplicate: which submission to keep. For each unknown response: the paired student it belongs to, or "leave out."
- **Source:** H6: Resolve Survey Response Exceptions, only when T8 found exceptions.

- **If a required input is missing or invalid:** If either snapshot is missing, T7 has already stopped the run. A response with a blank student ID is treated as an unknown response and goes to H6.

## 3. Outputs

### Output 1

- **Output name:** Matched survey data
- **Contents and format:** One record per paired student: student ID, name, role, pair number, mapped bargaining values (or blank), and match status (Matched, No response, or Resolved in H6).
- **Next task or recipient:** T9: Build Outcomes Workbook in Pairing Order.
- **Complete when:** Every paired student has exactly one record, and every response in the snapshot is used once, left out by the Instructor's decision, or listed as an exception.

### Output 2

- **Output name:** Survey exception list
- **Contents and format:** Produced only when needed: each duplicate (with all submissions, their times and values) and each unknown response (with the ID entered and the closest paired student IDs as suggestions).
- **Next task or recipient:** H6: Resolve Survey Response Exceptions (Instructor).
- **Complete when:** Every response not matched one-to-one appears on the list.

## 4. Planned Tools

### Tool 1

- **Tool name:** `match_survey_responses`
- **Input:** Survey snapshot; Pairing and template record; Exception decisions.
- **Output:** Matched survey data; Survey exception list.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that normalizes student IDs, applies the matching rules, and writes a Run Log entry with the counts of matched, missing, duplicate, and unknown responses.
- **Integration approach:** Direct integration.
- **Role in this task:** Matches responses by fixed rules and lists exceptions. It does not change any survey value.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 0
- **Retry only when:** Not applicable; the script works on data already in memory and gives the same result each time.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," record the error in the Run Log, and tell the Instructor in the chat. T9 does not run without complete matched data.
