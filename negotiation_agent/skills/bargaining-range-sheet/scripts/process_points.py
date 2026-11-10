"""Equity Splits process points sheet: the in-class Google Form, where each student rates each teammate.

Called by brs.py for --simulation ES (prepare, build, missing). The teams come from the roster's ES tab (the final
table if it has names, otherwise the draft). Her layout (Week 4 sheet): one row per rating, TRIO, the observer's
name and role, the partner's name and role (bold), the five scores, and TOTAL; sorted by trio, alternate trios
shaded. Added (assumptions): names and roles from the roster, a By Student tab, and yellow for students who
haven't rated every teammate.
"""
from __future__ import annotations

import csv
import re
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import brs
import nps_shared as ns
from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

FIXED = ["trio", "obs_first", "obs_last", "obs_role", "par_first", "par_last", "par_role"]


@dataclass
class Rating:
    row: int                       # row number in the CSV (the header is row 1)
    stamp: datetime | None
    typed: dict[str, str]
    scores: list
    observer: brs.Participant | None = None
    partner: brs.Participant | None = None
    team: int | None = None
    corrections: dict[str, str] = field(default_factory=dict)   # column key -> what was typed
    bad_scores: list[int] = field(default_factory=list)          # positions of scores kept as typed (light red)


# ---------------------------------------------------------------- reading the Form

def read_form(path: Path, sim: dict) -> tuple[list[list[str]], list[str], list[Rating]]:
    if not path.exists():
        raise ns.SkillError("file_missing", f"Could not find the Form export {path.name}.")
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    except PermissionError:
        raise ns.SkillError("file_locked", f"{path.name} is open in Excel. Close it and try again.")
    if not rows:
        raise ns.SkillError("survey_empty", f"{path.name} is empty.")
    header = [ns.clean(h) for h in rows[0]]
    lower = [h.lower() for h in header]
    cols = {}
    for key, prefix in sim["form"].items():
        hits = [i for i, h in enumerate(lower) if h.startswith(prefix.lower())]
        if not hits:
            raise ns.SkillError("survey_layout", f"The Form export has no column starting with '{prefix}'. The Form "
                                                 "may have been edited; the skill's settings need updating.",
                                {"columns": rows[0]})
        cols[key] = hits[0]
    score_cols = []
    for word in sim["scores"]:
        hits = [i for i, h in enumerate(header) if re.search(rf"\b{word}\b", h, re.I) and i not in cols.values()]
        if not hits:
            raise ns.SkillError("survey_layout", f"The Form export has no {word.title()} question.",
                                {"columns": rows[0]})
        score_cols.append(hits[0])
    out = []
    for n, row in enumerate(rows[1:], start=2):
        row = row + [""] * (len(header) - len(row))
        if not any(ns.clean(v) for v in row):
            continue
        out.append(Rating(n, parse_stamp(row[cols["timestamp"]]), {k: row[i] for k, i in cols.items()},
                          [row[i] for i in score_cols]))
    return rows, [header[i] for i in score_cols], out


def parse_stamp(text: str) -> datetime | None:
    for fmt in ("%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(ns.clean(text), fmt)
        except ValueError:
            continue
    return None


def score(text: str, low: int, high: int) -> tuple[object, bool]:
    """(value, ok). A whole number in range is a number; anything else is kept as typed and flagged."""
    typed = ns.clean(text)
    if re.fullmatch(r"\d+(\.0+)?", typed):
        value = int(float(typed))
        return value, low <= value <= high
    return (typed or None), False


# ---------------------------------------------------------------- matching ratings to teams

def similar(a: str, b: str) -> bool:
    """Close spellings of one name: "Boid"/"Boyd", "Sammantha"/"Samantha", "Sat"/"Sato"."""
    a, b = ns.normalize(a), ns.normalize(b)
    if not a or not b:
        return False
    if a == b or (min(len(a), len(b)) >= 3 and (a.startswith(b) or b.startswith(a))):
        return True
    if abs(len(a) - len(b)) > 2:
        return False
    prev = list(range(len(b) + 1))   # edit distance, at most 2 for a name of 4 letters or more
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= (1 if min(len(a), len(b)) < 6 else 2)


def find(first: str, last: str, people: list[brs.Participant]) -> tuple[brs.Participant | None, str]:
    """One person from a small list (a team, or the whole class): exact, nickname, then a close spelling.
    Returns the person and how ("exact", "nickname", "close"), or None and why not."""
    key = ns.name_key(first, last)
    exact = [p for p in people if ns.name_key(p.first, p.last) == key]
    if len(exact) == 1:
        return exact[0], "exact"
    nick = [p for p in people if ns.normalize(p.last) == ns.normalize(last) and ns.first_names_compatible(p.first, first)]
    if len(nick) == 1:
        return nick[0], "nickname"
    close = [p for p in people if (similar(p.first, first) or ns.first_names_compatible(p.first, first))
             and similar(p.last, last)]
    if len(close) == 1:
        return close[0], "close"
    return None, "more than one student fits" if len(exact + nick + close) > 1 else "no student fits"


def match_ratings(ratings: list[Rating], groups: dict, absent: list, args) -> tuple[list[Rating], list[dict], list[str]]:
    """Link every rating to an observer and a partner in the observer's team. Returns the ratings used, what needs
    her decision, and plain-language notes (duplicates)."""
    everyone = [p for g in groups.values() for p in g]
    team_of = {p.name: m for m, g in groups.items() for p in g}
    by_name = {p.name: p for p in everyone + absent}
    decided = {"observer": {}, "partner": {}}
    for kind, specs in (("observer", args.observer), ("partner", args.partner)):
        for spec in specs:
            row, _, name = spec.partition("=")
            if not row.strip().isdigit() or name.strip() not in by_name:
                raise ns.SkillError("bad_decision", f"--{kind} {spec}: give the Form row number and a name from the "
                                                    "ES tab ('Last, First').")
            decided[kind][int(row)] = by_name[name.strip()]
    skip = {int(x) for x in args.form_skip if x.strip().isdigit()}
    unresolved, used = [], []
    for r in ratings:
        if r.row in skip:
            continue
        typed_team = re.sub(r"\D", "", ns.clean(r.typed["trio"]))
        team = int(typed_team) if typed_team else None
        # The observer: anyone on the ES tab, by name; or, if the name is unclear, within the trio typed.
        obs, how = (decided["observer"][r.row], "decided") if r.row in decided["observer"] else \
            find(r.typed["obs_first"], r.typed["obs_last"], everyone)
        if not obs and team in groups:
            obs, how = find(r.typed["obs_first"], r.typed["obs_last"], groups[team])
        typed_obs = f"{ns.clean(r.typed['obs_first'])} {ns.clean(r.typed['obs_last'])}".strip()
        if not obs:
            unresolved.append({"type": "observer", "form_row": r.row, "typed_name": typed_obs,
                               "trio": ns.clean(r.typed["trio"]), "reason": how,
                               "suggestions": [p.name for p in everyone if similar(p.last, r.typed["obs_last"])
                                               or similar(p.first, r.typed["obs_first"])][:3]})
            continue
        if obs.name not in team_of:
            unresolved.append({"type": "observer", "form_row": r.row, "typed_name": typed_obs,
                               "reason": f"{obs.name} is listed as absent on the ES tab", "suggestions": []})
            continue
        r.observer, r.team = obs, team_of[obs.name]
        mates = [p for p in groups[r.team] if p is not obs]
        par, how = (decided["partner"][r.row], "decided") if r.row in decided["partner"] else \
            find(r.typed["par_first"], r.typed["par_last"], mates)
        typed_par = f"{ns.clean(r.typed['par_first'])} {ns.clean(r.typed['par_last'])}".strip()
        if not par:
            elsewhere, _ = find(r.typed["par_first"], r.typed["par_last"], everyone)
            reason = ("they rated themselves" if elsewhere is obs else
                      f"{elsewhere.name} is in trio {team_of[elsewhere.name]}, not {obs.name}'s trio {r.team}"
                      if elsewhere else how + f" in trio {r.team}")
            unresolved.append({"type": "partner", "form_row": r.row, "observer": obs.name, "typed_name": typed_par,
                               "reason": reason, "suggestions": [p.name for p in mates]})
            continue
        r.partner = par
        # Corrections, shown in orange with what was typed: trio, names (beyond case and spacing), roles.
        if ns.clean(r.typed["trio"]) != str(r.team):
            r.corrections["trio"] = ns.clean(r.typed["trio"])
        for prefix, person in (("obs", obs), ("par", par)):
            for part in ("first", "last"):
                typed = ns.clean(r.typed[f"{prefix}_{part}"])
                if ns.normalize(typed) != ns.normalize(getattr(person, part)):
                    r.corrections[f"{prefix}_{part}"] = typed
            if ns.normalize(r.typed[f"{prefix}_role"]) != ns.normalize(person.role):
                r.corrections[f"{prefix}_role"] = ns.clean(r.typed[f"{prefix}_role"])
        used.append(r)
    # Duplicates: the same observer rating the same partner twice. The latest is used.
    latest, notes = {}, []
    for r in used:
        k = (r.observer.name, r.partner.name)
        if k in latest:
            older, newer = sorted((latest[k], r), key=lambda x: (x.stamp or datetime.min, x.row))
            notes.append(f"{k[0]} rated {k[1]} twice (Form rows {older.row} and {newer.row}); the later one is used.")
            latest[k] = newer
        else:
            latest[k] = r
    return list(latest.values()), unresolved, notes


def expected_missing(groups: dict, used: list[Rating]) -> dict[str, list[str]]:
    """{observer: teammates they haven't rated yet}. Absent students aren't on any team, so aren't expected."""
    done = {(r.observer.name, r.partner.name) for r in used}
    out = {}
    for g in groups.values():
        for p in g:
            left = [q.name for q in g if q is not p and (p.name, q.name) not in done]
            if left:
                out[p.name] = left
    return out


# ---------------------------------------------------------------- writing the sheet

def write_main(ws, used: list[Rating], score_headers: list[str], sim: dict) -> dict:
    roles = sim["roles"]
    headers = ["TRIO", "OBSERVER: What is your first name?", "OBSERVER: What is your last name?",
               "OBSERVER: What was your role in this negotiation?",
               "PARTNER: What is the first name of the person you are assessing?",
               "PARTNER: What is the last name of the person you are assessing?",
               "PARTNER: What was the role of the person you are assessing?", *score_headers, "TOTAL"]
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[1].height = 90
    first_score = len(FIXED) + 1
    total_col = first_score + len(score_headers)
    low, high = sim["score_range"]
    expected = {}
    ordered = sorted(used, key=lambda r: (r.team, roles.index(r.partner.role), r.partner.name,
                                          roles.index(r.observer.role), r.observer.name))
    teams = sorted({r.team for r in ordered})
    for i, r in enumerate(ordered, start=2):
        values = [r.team, r.observer.first, r.observer.last, r.observer.role.title(),
                  r.partner.first, r.partner.last, r.partner.role.title()]
        for k, v in enumerate(values, start=1):
            ws.cell(i, k, v)
        for k, typed in enumerate(r.scores):
            value, ok = score(typed, low, high)
            cell = ws.cell(i, first_score + k, value)
            if not ok:
                cell.fill = brs.fill(brs.LIGHT_RED)
                cell.comment = Comment(f"Kept as typed: {ns.clean(typed) or '(blank)'}. Scores go from {low} to {high}.",
                                       brs.AUTHOR)
        ws.cell(i, total_col, f"=SUM({get_column_letter(first_score)}{i}:{get_column_letter(total_col - 1)}{i})")
        band = teams.index(r.team) % 2 == 0
        for k in range(1, total_col + 1):
            cell = ws.cell(i, k)
            if k in (5, 6, 7, 1, total_col):
                cell.font = Font(bold=True)
            if band and cell.fill.fgColor.rgb in (None, "00000000"):
                cell.fill = brs.fill(brs.BAND)
        for key, typed in r.corrections.items():
            cell = ws.cell(i, FIXED.index(key) + 1)
            cell.fill = brs.fill(brs.ORANGE)
            cell.comment = Comment(f"Typed: {typed or '(blank)'}\nCorrected from the ES tab.", brs.AUTHOR)
        expected.update({(i, k + 1): ws.cell(i, k + 1).value for k in range(len(values))})
    widths = [7, 12, 14, 12, 12, 14, 12] + [11] * len(score_headers) + [9]
    for k, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(k)].width = w
    ws.freeze_panes = "H2"
    return expected


def write_by_student(wb, main_title: str, groups: dict, absent: list, missing: dict, n_scores: int) -> None:
    ws = wb.create_sheet("By Student")
    ws.append(["TRIO", "FIRST", "LAST", "ROLE", "RATED", "OF", "NOT YET RATED", "RATINGS RECEIVED",
               "POINTS RECEIVED", "AVERAGE TOTAL"])
    for c in ws[1]:
        c.font = Font(bold=True)
    main = f"'{main_title}'"
    total = get_column_letter(len(FIXED) + n_scores + 1)
    r = 2
    for team, people in sorted(groups.items()):
        for p in people:
            expected = len(people) - 1
            left = missing.get(p.name, [])
            ws.append([team, p.first, p.last, p.role.title(), expected - len(left), expected, ", ".join(left),
                       f'=COUNTIFS({main}!$E:$E,B{r},{main}!$F:$F,C{r})',
                       f'=SUMIFS({main}!${total}:${total},{main}!$E:$E,B{r},{main}!$F:$F,C{r})',
                       f'=IFERROR(I{r}/H{r},"")'])
            if left:   # hasn't rated every teammate: she may want to chase them (Meeting 5)
                for c in ws[r]:
                    c.fill = brs.fill(brs.YELLOW)
            r += 1
    if absent:
        r += 1
        ws.cell(r, 1, brs.ABSENT_LABEL).font = Font(bold=True)
        for p in absent:
            r += 1
            ws.cell(r, 2, p.first), ws.cell(r, 3, p.last), ws.cell(r, 4, p.role.title())
    r += 2
    for color, text in ((brs.ORANGE, "Corrected from the ES tab (what was typed is in the cell's comment)"),
                        (brs.LIGHT_RED, "A score that isn't a whole number from 0 to 5, kept as typed"),
                        (brs.YELLOW, "Hasn't rated every teammate yet")):
        ws.cell(r, 1).fill = brs.fill(color)
        ws.cell(r, 2, text)
        r += 1
    for col, w in zip("ABCDEFGHIJ", (7, 12, 16, 10, 7, 5, 34, 10, 10, 10)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "B2"


# ---------------------------------------------------------------- the command

def now_value(r: Rating, key: str):
    if key == "trio":
        return r.team
    person = r.observer if key.startswith("obs") else r.partner
    value = getattr(person, key.split("_", 1)[1])
    return value.title() if key.endswith("role") else value


def run(args, mode: str, sim: dict) -> None:
    started = time.time()
    roster = Path(args.roster).expanduser().resolve()
    if not args.form:
        raise ns.SkillError("bad_option", f"{sim['name']} uses the in-class Google Form: pass --form with its CSV.")
    form_path = Path(args.form).expanduser().resolve()
    raw_rows, score_headers, ratings = read_form(form_path, sim)
    _, stage, groups, absent, warnings = brs.load_matches(roster, args.simulation, sim)
    used, unresolved, notes = match_ratings(ratings, groups, absent, args)
    missing = expected_missing(groups, used)
    low, high = sim["score_range"]
    corrected = [{"form_row": r.row, "student": r.observer.name, "column": k, "typed": v, "now": now_value(r, k)}
                 for r in used for k, v in r.corrections.items()]
    unclear = [{"form_row": r.row, "observer": r.observer.name, "partner": r.partner.name, "typed": ns.clean(t)}
               for r in used for t in r.scores if not score(t, low, high)[1]]
    students = sum(len(g) for g in groups.values())
    result = {"ok": True, "teams_from": stage, "teams": len(groups), "students": students, "absent": [p.name for p in absent],
              "form_rows": len(ratings), "ratings_used": len(used),
              "ratings_expected": sum(len(g) * (len(g) - 1) for g in groups.values()),
              "duplicates": notes, "corrected": corrected, "unclear_scores": unclear,
              "not_rated_everyone": {k: v for k, v in sorted(missing.items())},
              "unresolved": unresolved, "ready_to_build": not unresolved, "warnings": warnings}
    if mode == "missing":
        people = {p.name: p for g in groups.values() for p in g}
        emails = [people[n].email for n in sorted(missing) if people[n].email]
        ns.write_log(roster.parent, "T10 Process points not submitted (ES)",
                     f"{len(missing)} of {students} students haven't rated every teammate.")
        ns.emit({"ok": True, "teams_from": stage, "students": students,
                 "missing": {k: v for k, v in sorted(missing.items())}, "bcc": "; ".join(emails),
                 "unresolved": unresolved})
        return
    if mode != "build":
        ns.write_log(roster.parent, "Prepare process points sheet (ES)",
                     f"{form_path.name}: {len(used)} ratings of {result['ratings_expected']} expected, "
                     f"{len(unresolved)} unresolved, teams from the {stage} table.")
        ns.emit(result)
        return
    if unresolved:
        raise ns.SkillError("unresolved_responses", "Some Form rows need the instructor's decision first.",
                            {"unresolved": unresolved})
    course = args.course or brs.course_from_roster(roster)
    if not course:
        raise ns.SkillError("course_unknown", "Could not tell the course and term from the roster file name. "
                                              "Pass --course, e.g. 'BUS 4489 F26'.")
    out = form_path.parent / f"{course} Week {args.week} - {sim['file_title']}.xlsx"
    previous = ns.backup(out, "replaced") if out.exists() else None
    wb = Workbook()
    ws = wb.active
    ws.title = brs.safe_title(f"Week {args.week} Process Points")
    expected = write_main(ws, used, score_headers, sim)
    write_by_student(wb, ws.title, groups, absent, missing, len(score_headers))
    raw = wb.create_sheet("Raw")
    for row in raw_rows:
        raw.append(row)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / out.name
        wb.save(tmp_path)
        check = load_workbook(tmp_path).worksheets[0]
        mismatched = [check.cell(r, c).coordinate for (r, c), v in expected.items() if check.cell(r, c).value != v]
        if mismatched:
            raise ns.SkillError("readback_mismatch", "Some values did not save correctly; the sheet was not created.",
                                {"cells": mismatched})
        try:
            shutil.copyfile(tmp_path, out)
        except PermissionError:
            raise ns.SkillError("file_locked", f"{out.name} is open in Excel. Close it and try again.")
    result.update({"workbook": str(out), "previous_version_backup": str(previous) if previous else None,
                   "seconds": round(time.time() - started, 1)})
    warning = ns.write_log(roster.parent, "Build process points sheet (ES)",
                           f"{out.name} from the {stage} table: {len(used)} ratings, {len(missing)} students who "
                           f"haven't rated every teammate. Previous version: {previous.name if previous else 'none'}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)
