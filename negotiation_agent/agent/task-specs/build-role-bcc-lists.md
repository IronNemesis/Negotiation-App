# Build Role BCC Lists Task Specification

## Basic Information

- **Task ID:** T5
- **Task name:** Build Role BCC Lists
- **Task type:** Act
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

The Instructor emails each role its packet in one email, with all students in that role on BCC. T5 saves her the step of finding and copying those addresses.

For each role, it produces a ready-to-paste list of Cal Poly emails separated by semicolons, which Outlook accepts in the BCC field. The list includes every student in that role in the approved draft, second same-role students included. The lists go in the chat and in a small text file next to the workbook, so she can copy from either.

T5 does not send anything and does not attach packets. Students learn their partners in class, so no partner information is included.

## 2. Inputs

### Input 1

- **Input name:** Written draft matches
- **Contents and format:** The draft matches as written by T4.
- **Source:** T4: Write Draft Matches.

### Input 2

- **Input name:** Class snapshot
- **Contents and format:** Each student's Cal Poly email from the class list.
- **Source:** T1: Read Class List and Simulation Tab.

- **If a required input is missing or invalid:** A student with no email on the class list is left off the list and named in the chat, so she can add them by hand.

## 3. Outputs

### Output 1

- **Output name:** Role BCC lists
- **Contents and format:** One block per role (for example "BUYER (19 students): a@calpoly.edu; b@calpoly.edu; …"), in the chat and in `<code> role emails <date>.txt` next to the workbook.
- **Next task or recipient:** H3: Send Role Emails.
- **Complete when:** Every student in the draft appears in exactly one role's list, or is named as missing an email, and the counts match the draft.

## 4. Planned Tools

### Tool 1

- **Tool name:** `build_bcc_lists`
- **Input:** Written draft matches; Class snapshot.
- **Output:** Role BCC lists.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that groups emails by role and writes the text file.
- **Integration approach:** Direct integration.
- **Role in this task:** Prepares address lists. It has no access to Outlook and cannot send email.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 1
- **Retry only when:** The text file can't be written because a file with that name is open. Retry once with a time-stamped name.
- **On timeout, exhausted retries, or an error that cannot be retried:** Show the lists in the chat only, log the problem, and tell the Instructor the text file wasn't saved.
