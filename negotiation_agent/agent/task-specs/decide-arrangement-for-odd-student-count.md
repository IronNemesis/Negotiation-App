# Decide Arrangement for Odd Student Count Task Specification

## Basic Information

- **Task ID:** H3
- **Task name:** Decide Arrangement for Odd Student Count
- **Task type:** Decide
- **Task owner:** Instructor.

## 1. Task Description

When an odd number of students is attending, one student cannot be paired, and the Instructor decides how to handle it. The agent offers three options:
1. One group of three, where she chooses which role is doubled.
2. She partners with one student herself.
3. One student observes this round.

For options 2 and 3, the agent suggests the student with the fewest past negotiations in this section, but she can name anyone. This is a teaching decision that depends on the class and the simulation, so the agent never makes it on its own.

## 2. Inputs

### Input 1

- **Input name:** Attendance list
- **Contents and format:** Attending students and the odd attending count, plus each student's number of past negotiations from the section snapshot.
- **Source:** T2: Build Attendance List from Absences; T1: Retrieve Section Roster and Pairing History.

### Input 2

- **Input name:** Arrangement decision
- **Contents and format:** The Instructor's reply in the chat: the chosen option, plus the doubled role (option 1) or the named student (options 2 and 3).
- **Source:** Instructor.

- **If a required input is missing or invalid:** A decision that names a student who is not attending is shown back to her with the attending list. T3 does not run until a complete decision is recorded.

## 3. Outputs

### Output 1

- **Output name:** Odd-count arrangement
- **Contents and format:** Structured record: chosen option, doubled role or named student, and a Run Log entry recording the decision.
- **Next task or recipient:** T3: Generate Unique Pairs and Assign Roles.
- **Complete when:** The decision includes every detail T3 needs to apply it.

## 4. Planned Tools

### Tool 1

- **Tool name:** `record_odd_count_arrangement`
- **Input:** Attendance list; Arrangement decision.
- **Output:** Odd-count arrangement.
- **Implementation Route:** The agent's chat conversation with the Instructor in the Claude desktop app, plus a local script that writes the decision to the Run Log.
- **Integration approach:** Direct integration.
- **Role in this task:** Presents the options and records her choice. It does not pick an option itself.
- **Task timeout:** No fixed deadline; the run waits for the Instructor.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If the Instructor ends the session without deciding, the Run Log shows the run as "Waiting on Instructor: odd student count," and no pairing is produced.
