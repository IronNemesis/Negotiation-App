# Record Gender and Consent Task Specification

## Basic Information

- **Task ID:** T12
- **Task name:** Record Gender and Consent
- **Task type:** Remember
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

In Week 1, students take a baseline survey that includes informed consent for the research and their gender. The Used Car experimental conditions (I/C) are balanced by gender, and students who decline consent are paired together, so both are needed on the roster (Meeting 4).

T12 reads the baseline export **once** and records, for every student on the class list:
- **Gender:** `M`, `F`, or `Other`.
- **Consent:** `Yes`, `No`, `Excluded` (chose Other for gender, so excluded from the research), or `No (no survey)` (didn't take the survey, which counts as declined).

These go in two columns headed `Gender` and `Consent`, just after `Email` on the class list tab. Consent is recorded only there.

Responses are matched to students by name. Anything unclear is her decision, and the latest response counts if a student took it twice. The rest of the baseline survey (the research items in the codebook) is not used yet.

## 2. Inputs

- **Baseline export:** the Week 1 Qualtrics CSV, downloaded with number codes. Source: the Instructor.
- **Class list:** the attendance tab of the roster. Source: her roster workbook.
- **Decisions:** whose response an unclear one is. Source: the Instructor (H4-style).
- **If a required input is missing or invalid:**
  - An export with answer text instead of codes, or without the consent, name or gender columns: T12 stops and says so.
  - A tab where inserting columns could break something (formulas, merged cells, validation, tables, or references from other tabs): T12 asks her to insert the two blank columns herself.

## 3. Outputs

- **Preview:** counts, plus who declined, who is excluded, who didn't take the survey, and duplicates. Next: the Instructor confirms.
- **Updated class list:** Gender and Consent filled in, with a backup and a log entry. Complete when every student has a Consent value, and every other cell is exactly where it was or two columns to the right.

## 4. Planned Tools

- **Tool:** `pairing.py baseline` / `write-baseline`, a Python script bundled with the skill.
  - Backs up the workbook, writes, then checks every cell on every tab against the backup.
  - Restores the backup on any difference.
- **Task timeout:** 30 seconds.
- **Retries:** once, if the workbook is open in Excel.
