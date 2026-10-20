# List Survey Non-Respondents Task Specification

## Basic Information

- **Task ID:** T10
- **Task name:** List Survey Non-Respondents
- **Task type:** Retrieve
- **Task owner:** Negotiation Pairing Solution (`bargaining-range-sheet` skill); the Instructor is accountable.

## 1. Task Description

Before class, the Instructor emails students who haven't submitted the survey (Meeting 3). T10 tells her who they are, so she doesn't have to compare the export with her class list by hand.

T10 runs the same cleaning (T6) and matching (T7) as the bargaining range sheet, using the latest export she has downloaded, and lists every student in the current matches with no matched response:
- The names, sorted alphabetically, and a ready-to-paste BCC list of their Cal Poly emails, separated by semicolons as for the role emails (T5).
- Responses that couldn't be matched to a student yet (for example a misspelled name), listed separately with their suggestions. One of them may belong to a student on the list, so she can check before emailing them.
- Students who submitted more than once are not listed: they have answered.
- Absent students (`_0`, after the absence update) are not listed, since they won't negotiate.

T10 accepts the same decisions as T7 (`--assign`, `--leave-out`, and so on), so once she has resolved a misspelled name, that student drops off the list. It writes nothing to her workbook and sends nothing.

## 2. Inputs

### Input 1

- **Input name:** Qualtrics export
- **Contents and format:** The latest CSV she downloaded from Qualtrics.
- **Source:** The Instructor.

### Input 2

- **Input name:** Current matches
- **Contents and format:** The final table if it has names, otherwise the draft table, plus the class list for emails.
- **Source:** Her roster workbook, read as in T7.

### Input 3

- **Input name:** Decisions (optional)
- **Contents and format:** Any H4 decisions she has already made.
- **Source:** H4: Resolve Survey Matches.

- **If a required input is missing or invalid:** The same as T6 and T7: a missing or changed export stops the run (H1). A student with no email on the class list is named, so she can reach them another way.

## 3. Outputs

### Output 1

- **Output name:** Non-respondent list
- **Contents and format:** In the chat and in `<code> survey missing <date>.txt` next to the roster workbook: the names, the BCC list, and any unmatched responses.
- **Next task or recipient:** The Instructor, who sends her own reminder email.
- **Complete when:** Every student in the current matches either has a matched response, is part of an unresolved duplicate, or is on the list; and the BCC list has one address per listed student with an email.

## 4. Planned Tools

### Tool 1

- **Tool name:** `brs.py missing`
- **Input:** Qualtrics export; Current matches; Decisions.
- **Output:** Non-respondent list.
- **Implementation Route:** Functions/scripts; the bargaining range sheet script, reusing its cleaning and matching.
- **Integration approach:** Direct integration.
- **Role in this task:** Prepares a list. It has no access to Outlook or Qualtrics and cannot send email.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 1
- **Retry only when:** The text file can't be written because it is open. Show the list in the chat only.
- **On timeout, exhausted retries, or an error that cannot be retried:** Log the problem and tell the Instructor.
