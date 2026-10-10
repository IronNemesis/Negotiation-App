# Match Survey Responses to Students Task Specification

## Basic Information

- **Task ID:** T7
- **Task name:** Match Survey Responses to Students
- **Task type:** Reason
- **Task owner:** Negotiation Pairing Solution (`bargaining-range-sheet` skill); the Instructor is accountable.

## 1. Task Description

There are no student ID numbers, so T7 connects each survey response to a student in the current matches using names and emails. Students type their own names (sometimes with nicknames, stray spaces, or lowercase) and often give a personal email. Wrong numbers in the debrief would mislead the class, so T7 matches only when it is confident and asks the Instructor otherwise.

The current matches come from the simulation tab:
- **before class,** the draft table;
- **after the absence update,** the final table.

A response is matched to a student when exactly one student fits the first rule that applies:
1. **Email:** the response email equals the student's Cal Poly email on the class list (ignoring case).
2. **Full name:** first and last name equal the class-list name, ignoring case, spaces, and accents.
3. **Nickname:** the last name matches exactly, the first name is a known nickname or shortened form of the class-list first name (Andrew/Andy, Katherine/Katie), and no other student shares that last name.

Anything else is unresolved and goes to H4, with the closest students suggested. Examples: two responses claiming the same student, a response that fits no one, or a response that fits more than one student.

Further rules:
- **Role conflict:** if a student's survey role differs from their assigned role, the assigned role wins and the `ROLE` cell is highlighted light red with a comment, because students sometimes click the wrong option.
- **No response:** students with no matched response keep their place on the sheet with blank answers.
- **Absent students:** after the absence update, a response from an absent student is left off the sheet and listed in the summary (assumption; see open questions).

## 2. Inputs

### Input 1

- **Input name:** Cleaned responses
- **Contents and format:** From T6.
- **Source:** T6: Clean Survey Export.

### Input 2

- **Input name:** Current matches and class list
- **Contents and format:** The draft or final matches from the simulation tab, the absent students (`_0`), and each student's name and Cal Poly email from the class list.
- **Source:** The roster workbook, read read-only with the same reader T1 uses.

### Input 3

- **Input name:** Match decisions
- **Contents and format:** The Instructor's answers for unresolved responses: which student a response belongs to, which of two submissions to use, or "leave out."
- **Source:** H4: Resolve Survey Matches, only when needed.

- **If a required input is missing or invalid:** If the simulation tab has neither a draft nor a final table filled in, T7 stops and tells the Instructor to draft the matches first (Stage 1).

## 3. Outputs

### Output 1

- **Output name:** Matched responses
- **Contents and format:** One record per student in the current matches: match number, role, and their cleaned response (or none), with how it was matched (email, name, nickname, or her decision) and any role conflict.
- **Next task or recipient:** T8: Build Bargaining Range Sheet.
- **Complete when:** Every response is matched to exactly one student, left out by her decision, or listed as unresolved, and no student has more than one response.

### Output 2

- **Output name:** Unresolved responses
- **Contents and format:** Produced only when needed: each unresolved response with the name and email typed, the reason, and up to three suggested students.
- **Next task or recipient:** H4: Resolve Survey Matches.
- **Complete when:** Every response not matched by rules 1–3 is listed.

## 4. Planned Tools

### Tool 1

- **Tool name:** `match_responses`
- **Input:** Cleaned responses; Current matches and class list; Match decisions.
- **Output:** Matched responses; Unresolved responses.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill, with a small nickname list and name normalization (accents, spacing, case). It logs how every response was matched.
- **Integration approach:** Direct integration.
- **Role in this task:** Matches by fixed rules and lists everything else. It never attaches a response to a student on a guess.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 0
- **Retry only when:** Not applicable; the rules give the same result every time.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," log the error, and tell the Instructor. T8 does not run.
