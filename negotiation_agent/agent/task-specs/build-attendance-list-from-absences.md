# Build Attendance List from Absences Task Specification

## Basic Information

- **Task ID:** T2
- **Task name:** Build Attendance List from Absences
- **Task type:** Reason
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T2 turns the Instructor's list of absent students, written however she likes (names, nicknames, emails, or student IDs), into a definite list of students to pair. It matches each absence to the roster using fixed rules, in order: exact student ID, exact email address, then exact full name ignoring capitalization and extra spaces. An entry that matches exactly one student is applied. An entry that matches no one, or more than one student, is never applied on a guess; T2 lists the closest roster names as suggestions and sends the entry to H2: Confirm Unmatched Absences. This keeps an absent student from being paired and keeps a present student from being left out. T2 then counts the attending students and checks whether the count is even.

## 2. Inputs

### Input 1

- **Input name:** Section snapshot
- **Contents and format:** Pairable student list from T1.
- **Source:** T1: Retrieve Section Roster and Pairing History.

### Input 2

- **Input name:** Absence list
- **Contents and format:** Free-text list of absent students from the Instructor's run request, one or more entries. "None" or an empty list means everyone is present.
- **Source:** The Instructor, in the run request.

### Input 3

- **Input name:** Absence decisions
- **Contents and format:** For each unmatched entry: the roster student it refers to, or "ignore this entry."
- **Source:** H2: Confirm Unmatched Absences, only when T2 found unmatched entries.

- **If a required input is missing or invalid:** If the section snapshot is missing, T1 has already stopped the run. If the Instructor did not mention absences at all, T2 asks once in the chat whether anyone is absent rather than assuming everyone is present.

## 3. Outputs

### Output 1

- **Output name:** Attendance list
- **Contents and format:** Structured record: run ID, attending students (student ID, name), absent students with the entry and rule that matched each, attending count, and whether the count is even.
- **Next task or recipient:** T3: Generate Unique Pairs and Assign Roles, or H3: Decide Arrangement for Odd Student Count when the count is odd.
- **Complete when:** Every absence entry is either matched to exactly one student or resolved in H2, and attending plus absent students equals the pairable student list.

### Output 2

- **Output name:** Unmatched absence list
- **Contents and format:** Structured record produced only when needed: each unmatched or ambiguous entry, the reason, and up to three suggested roster names.
- **Next task or recipient:** H2: Confirm Unmatched Absences (Instructor).
- **Complete when:** Every entry not matched by an exact rule appears on the list.

## 4. Planned Tools

### Tool 1

- **Tool name:** `match_absences`
- **Input:** Section snapshot; Absence list; Absence decisions.
- **Output:** Attendance list; Unmatched absence list.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that applies the exact-match rules and ranks close name matches as suggestions only. Writes a Run Log entry listing every match and the rule used.
- **Integration approach:** Direct integration.
- **Role in this task:** Applies exact matches and proposes suggestions for everything else. It never applies a suggested match without the Instructor's decision.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 0
- **Retry only when:** Not applicable; the script works on data already in memory and gives the same result each time.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," record the error in the Run Log, and tell the Instructor in the chat. T3 does not run without a complete attendance list.
