# Report Absences Task Specification

## Basic Information

- **Task ID:** H5
- **Task name:** Report Absences
- **Task type:** Decide
- **Task owner:** Instructor.

## 1. Task Description

At the start of class, the Instructor tells Claude who is absent, in whatever form is natural ("Evans and Silva aren't here", or "nobody's missing"). Some students email her in advance; most absences only become clear when class starts.

Claude matches each name to the class list:
- exact full name or email first;
- then a last name or first name that fits exactly one student.

Anything that fits no one, or more than one student, is shown back to her with suggestions instead of guessed. A wrong guess would move a present student out of their match.

Saying nobody is absent is a valid answer. T9 then writes the draft as the final table.

## 2. Inputs

### Input 1

- **Input name:** Absence report
- **Contents and format:** Free-text list of absent students, or "nobody."
- **Source:** Instructor, in the chat.

### Input 2

- **Input name:** Class list and draft matches
- **Contents and format:** Names and emails from the class list; the current draft table.
- **Source:** T1: Read Class List and Simulation Tab.

- **If a required input is missing or invalid:** If she starts the absence update without naming anyone, Claude asks once who is absent rather than assuming everyone is present. A name that matches a student who isn't in the draft at all is pointed out, since that student may already be recorded as absent.

## 3. Outputs

### Output 1

- **Output name:** Absent students
- **Contents and format:** The matched absent students (name, email, draft match), with how each was matched, recorded in the log.
- **Next task or recipient:** T9: Apply Absences and Write Final Matches.
- **Complete when:** Every name she gave is matched to exactly one student or resolved with her.

## 4. Planned Tools

### Tool 1

- **Tool name:** `match_absences`
- **Input:** Absence report; Class list and draft matches.
- **Output:** Absent students.
- **Implementation Route:** The chat conversation in the Claude desktop app, plus a Python script bundled with the skill that applies the matching rules and logs the result.
- **Integration approach:** Direct integration.
- **Role in this task:** Matches names by fixed rules and asks about the rest.
- **Task timeout:** No fixed deadline; this happens in class, and Claude keeps questions to one short message.
- **Maximum retries:** Not applicable — manual task.
- **Retry only when:** Not applicable.
- **On timeout, exhausted retries, or an error that cannot be retried:** If she ends the session before the absences are settled, nothing is written, and the log shows "Waiting on Instructor: absences."
