"""Negotiation pairing: draft matches, role BCC lists, and the in-class absence update.

Commands (task IDs refer to negotiation_agent/agent/task-specs):
  snapshot     T1       what the workbook holds for this simulation; writes nothing
  draft        T2 + T3  preview the draft with her alphabetical method, with checks; writes nothing
  write-draft  T4       write the approved draft into the simulation tab's draft table
  check        T3       re-check the draft table as it stands (after she edits it in Excel)
  bcc          T5       one BCC email list per role, in the output and in a text file
  roles-sent   H3       record that role emails went out (roles are locked from then on)
  absences     T9       propose the final matches for the absent students; writes nothing
  write-final  T9       write the confirmed final matches into the final table
  log                   record one of her decisions in the log
  baseline              read the Week 1 baseline survey: each student's gender and consent; writes nothing
  write-baseline        write Gender and Consent into two columns just after Email on the class list

Every command prints one JSON object. "ok": false comes with an "error" code and a plain-language "message".
Names are given as on her class list ("Last, First"); absences may be given however she said them.
"""
from __future__ import annotations

import argparse
import csv
from copy import copy
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nps_shared as ns  # noqa: E402
from openpyxl import load_workbook  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

SETTINGS = json.loads((HERE / "simulations.json").read_text(encoding="utf-8"))
MAX_GROUP = 3
DRAFT_METHODS = ("alphabetical-halves", "rotate-second-half")


# ---------------------------------------------------------------- loading

@dataclass
class Person:
    name: str                 # the name to write: class-list name when linked, otherwise as on the tab
    tab_name: str             # as on the simulation tab ("" for drafts computed from the class list)
    role: str
    student: ns.Student | None
    link: str                 # "exact", "email", "nickname", "confirmed", "likely", "none"

    @property
    def key(self) -> str:
        return self.student.key if self.student else ns.class_name_key(self.name)

    @property
    def email(self) -> str:
        return self.student.email if self.student else ""


class Context:
    def __init__(self, args):
        self.roster = Path(args.roster).expanduser().resolve()
        self.code = args.simulation
        if self.code not in SETTINGS:
            raise ns.SkillError("simulation_unknown", f"No settings for simulation '{self.code}'.",
                                {"known": sorted(SETTINGS)})
        self.sim = SETTINGS[self.code]
        self.roles = self.sim["roles"]
        self.wb = ns.open_workbook(self.roster)
        self.class_tab, self.students, self.class_warnings = ns.read_class_list(self.wb)
        self.tab = ns.read_sim_tab(self.wb, self.code, self.roles)
        self.history, self.unlinked_history = ns.read_pair_history(self.wb, exclude_code=self.code).linked_to_class(
            self.students)
        self.solo = solo_history(self.wb, self.code, self.students)
        self.baseline = read_baseline_columns(self.wb, self.class_tab, self.students)
        # Experimental conditions (Used Car): only once gender and consent are on the class list (T12).
        self.conditions = self.sim.get("conditions") if self.baseline else None
        self.same_person = {}
        for spec in getattr(args, "same_person", []) or []:
            tab_name, _, class_name = spec.partition("=")
            student = next((s for s in self.students if s.name == class_name.strip()), None)
            if not student:
                raise ns.SkillError("bad_option", f"--same-person {spec}: '{class_name.strip()}' is not on the class list.")
            self.same_person[ns.class_name_key(tab_name)] = student

    def by_name(self, name: str) -> ns.Student:
        res = ns.resolve_class_name(name, self.students)
        if res.confident:
            return res.student
        raise ns.SkillError("unknown_student", f"'{name}' doesn't match exactly one student on the class list.",
                            {"suggestions": [s.name for s in res.candidates] or ([res.student.name] if res.student else [])})

    def person_from_tab(self, m: ns.Member) -> Person:
        if ns.class_name_key(m.name) in self.same_person:
            s = self.same_person[ns.class_name_key(m.name)]
            return Person(s.name, m.name, m.role, s, "confirmed")
        res = ns.resolve_class_name(m.name, self.students, m.email)
        if res.confident:
            return Person(res.student.name, m.name, m.role, res.student, res.how)
        return Person(m.name, m.name, m.role, res.student if res.how == "likely" else None, res.how)

    def tab_groups(self, members: list[ns.Member]) -> dict[int, list[Person]]:
        return {match: [self.person_from_tab(m) for m in ms] for match, ms in self.tab.groups(members).items()}

    def log(self, step: str, details: str) -> str | None:
        return ns.write_log(self.roster.parent, f"{step} ({self.code})", details)


def read_baseline_columns(wb, tab: str, students: list[ns.Student]) -> dict[str, tuple[str, str]] | None:
    """{student key: (gender, consent)} from the class list's Gender and Consent columns, or None if not there."""
    ws = wb[tab]
    found = ns.find_header_row(ws, ["student name", "email"])
    if not found:
        return None
    hr, headers = found
    g, c = headers.get("gender"), headers.get("consent")
    if not (g and c):
        return None
    return {st.key: (ns.clean(ws.cell(st.row, g).value), ns.clean(ws.cell(st.row, c).value)) for st in students}


def draft_conditions(ctx) -> dict[int, str]:
    """{match: condition} from the CONDITION column next to the draft table, if there is one."""
    ws, tab = ctx.wb[ctx.code], ctx.tab
    col = next((c for c in range(1, ws.max_column + 2) if ns.clean(ws.cell(tab.draft_header, c).value).upper()
                == "CONDITION"), None)
    if not col:
        return {}
    out, current = {}, None
    for m in tab.draft_members:
        current = m.match if m.match is not None else current
        label = ns.clean(ws.cell(m.row, col).value).upper()
        if m.match is not None and label:
            out[m.match] = label
    return out


def solo_history(wb, current: str, students: list[ns.Student]) -> dict[str, list[str]]:
    """Who has already been "the 1" in a 1v2: alone on their side of a three-person match, on an earlier tab."""
    out: dict[str, list[str]] = {}
    for code, sim in SETTINGS.items():
        if code == current or code not in wb.sheetnames:
            continue
        try:
            tab = ns.read_sim_tab(wb, code, sim["roles"])
        except ns.SkillError:
            continue
        if not tab.final_members:
            continue
        for match, members in tab.groups(tab.final_members).items():
            alone = solo_of(members, sim["roles"])
            if alone:
                res = ns.resolve_class_name(alone.name, students, alone.email)
                if res.confident:
                    out.setdefault(res.student.key, []).append(f"{code}_{match}")
    return out


def solo_of(people: list, roles: list[str]):
    """The student alone on their side of a three-person match (the "1" in a 1v2), or None."""
    if len(people) != 3:
        return None
    for role in roles:
        alone = [p for p in people if p.role == role]
        if len(alone) == 1:
            return alone[0]
    return None


def table_preview(groups: dict[int, list[Person]], roles: list[str], conditions: dict[int, str] | None = None) -> list[dict]:
    return [{"match": m, **{r: [p.name for p in people if p.role == r] for r in roles},
             **({"condition": conditions.get(m, "")} if conditions else {})}
            for m, people in sorted(groups.items())]


# ---------------------------------------------------------------- T3: checks

def check_groups(ctx: Context, groups: dict[int, list[Person]], absent: list[Person], stage: str,
                 draft_roles: dict[str, str] | None = None) -> dict:
    errors, warnings = [], []
    seen: dict[str, int] = {}
    absent_keys = {p.key for p in absent}
    for match, people in sorted(groups.items()):
        roles = [p.role for p in people]
        for role in ctx.roles:
            if role not in roles:
                errors.append(f"Match {match} has no {role.title()}.")
        if len(people) > MAX_GROUP:
            errors.append(f"Match {match} has {len(people)} students; the most is {MAX_GROUP}.")
        for p in people:
            if p.key in seen:
                errors.append(f"{p.name} appears twice: matches {seen[p.key]} and {match}.")
            seen[p.key] = match
            if p.key in absent_keys:
                errors.append(f"{p.name} is marked absent but is in match {match}.")
            if p.link == "likely":
                errors.append(f"'{p.tab_name}' on the {ctx.code} tab isn't on the class list; it may be "
                              f"{p.student.name}. Confirm it's the same person.")
            elif p.link == "none":
                message = f"'{p.tab_name or p.name}' is in match {match} but isn't on the class list"
                if stage == "final":
                    errors.append(message + " (dropped the class, or a different spelling?).")
                else:  # a student who dropped after the draft is treated as absent at the absence step
                    warnings.append(message + ". If they dropped the class, they'll be listed as absent in class; "
                                              "if it's a different spelling, correct the name.")
            if draft_roles is not None and p.key in draft_roles and draft_roles[p.key] != p.role:
                errors.append(f"{p.name} was a {draft_roles[p.key].title()} in the draft and can't become a "
                              f"{p.role.title()}: role packets have already gone out.")
        alone = solo_of(people, ctx.roles)
        if alone and ctx.solo.get(alone.key):
            warnings.append(f"{alone.name} faces two partners alone in match {match} and already did in "
                            f"{', '.join(ctx.solo[alone.key])}.")
        for a, b in combinations(people, 2):
            shared = ctx.history.shared_ids(a.key, b.key)
            if shared:
                warnings.append(f"Repeat partners in match {match}: {a.name} and {b.name} were already together "
                                f"({', '.join(shared)}).")
    for s in ctx.students:
        if s.key not in seen and s.key not in absent_keys:
            message = f"{s.name} is on the class list but not in any match."
            (errors if stage == "final" else warnings).append(
                message + (" Report them as absent if they aren't in class." if stage == "final"
                           else " Were they already known to be absent?"))
    return {"errors": errors, "warnings": warnings,
            "summary": f"{len(errors)} errors, {len(warnings)} warnings"}


# ---------------------------------------------------------------- T2: drafting

def match_entry(entry: str, people: list[Person]) -> tuple[Person | None, list[Person], str]:
    """Match how she named an absent student to one person: email, full name, then a unique last or first name."""
    e = ns.normalize(entry.replace(",", " ")).replace(",", "")
    words = e.split()
    rules = [
        ("email", lambda p: p.email and p.email == entry.strip().lower()),
        ("full name", lambda p: sorted(ns.normalize(p.name.replace(",", " ")).split()) == sorted(words)),
        ("last name", lambda p: ns.normalize(ns.split_class_name(p.name)[1]) == e),
        ("first name", lambda p: ns.normalize(ns.split_class_name(p.name)[0]) == e),
    ]
    for rule, test in rules:
        hits = [p for p in people if test(p)]
        if len(hits) == 1:
            return hits[0], [], rule
        if len(hits) > 1:
            return None, hits, rule
    loose = [p for p in people if any(w in ns.normalize(p.name.replace(",", " ")).split() for w in words)]
    return None, loose[:4], "none"


def resolve_entries(entries: list[str], people: list[Person]) -> tuple[list[Person], list[dict]]:
    found, problems = [], []
    for entry in entries:
        if not entry.strip():
            continue
        person, candidates, rule = match_entry(entry, people)
        if person:
            found.append(person)
        else:
            problems.append({"entry": entry, "reason": "more than one student fits" if candidates and rule != "none"
                             else "no student fits", "suggestions": [p.name for p in candidates]})
    return found, problems


def compute_draft(ctx: Context, args) -> tuple[dict[int, list[Person]], list[Person]]:
    method = ctx.sim.get("draft_method")
    if method not in DRAFT_METHODS:
        raise ns.SkillError("draft_method_unknown", f"Drafting {ctx.sim['name']} isn't supported yet; only "
                                                    "simulations with a confirmed drafting method can be drafted.")
    everyone = [Person(s.name, "", "", s, "exact") for s in ctx.students]
    absent, problems = resolve_entries(args.absent, everyone)
    if problems:
        raise ns.SkillError("absence_unclear", "Some absent students couldn't be matched to one student.",
                            {"unclear": problems})
    absent_keys = {p.key for p in absent}
    ordered = sorted((s for s in ctx.students if s.key not in absent_keys), key=lambda s: s.key)
    if len(ordered) < 2:
        raise ns.SkillError("too_few_students", "Fewer than two students are left to match.")
    conditions: dict[int, str] = {}
    if method == "alphabetical-halves" and ctx.conditions:
        groups, conditions, notes = draft_with_conditions(ctx, ordered)
        side_notes = []
    elif method == "alphabetical-halves":
        half = len(ordered) // 2
        left, right, side_notes = ordered[:half], ordered[half:], []
    else:
        # Her later-simulation method: everyone keeps their side from the earlier simulation; the right column
        # moves down one and the bottom student goes to the top.
        left, right, side_notes = sides_from_previous(ctx, ordered)
        right = right[-1:] + right[:-1]
    if not conditions:
        groups, notes = pair_sides(ctx, left, right)
    notes = side_notes + notes
    for spec in args.swap:
        names = [n.strip() for n in spec.split(";")]
        if len(names) != 2:
            raise ns.SkillError("bad_option", f"--swap '{spec}' needs two names separated by ';'.")
        a, b = (ctx.by_name(n) for n in names)
        pa = next((m, p) for m, ps in groups.items() for p in ps if p.key == a.key)
        pb = next((m, p) for m, ps in groups.items() for p in ps if p.key == b.key)
        (ma, person_a), (mb, person_b) = pa, pb
        ia, ib = groups[ma].index(person_a), groups[mb].index(person_b)
        groups[ma][ia] = Person(b.name, "", person_a.role, b, "exact")
        groups[mb][ib] = Person(a.name, "", person_b.role, a, "exact")
    return groups, [Person(p.name, "", "", p.student, "exact") for p in absent], notes, conditions


def draft_with_conditions(ctx: Context, ordered: list[ns.Student]) -> tuple[dict, dict[int, str], list[str]]:
    """Used Car with experimental conditions (Meeting 4; assumptions to confirm with her):
    1. Students who didn't consent (No, no survey, or Excluded) are matched with each other.
    2. Everyone else: within each gender, alphabetically, the first half is the first condition (I) and the
       second half the second (C); an odd one out alternates between conditions across genders.
    3. Within each group, her usual method: first half Buyers, second half Sellers, matched in order.
    Matches are numbered condition by condition; each decliners' match takes the condition with fewer students."""
    first, second = ctx.conditions
    info = ctx.baseline
    research = [s for s in ordered if info.get(s.key, ("", ""))[1] == "Yes"]
    decliners = [s for s in ordered if s not in research]
    notes = []
    by_gender: dict[str, list] = {}
    for s in research:
        by_gender.setdefault(info[s.key][0] or "unknown", []).append(s)
    cond = {first: [], second: []}
    extra_to_first = True
    for gender in sorted(by_gender):
        people = by_gender[gender]
        k = len(people) // 2 + (len(people) % 2 if extra_to_first else 0)
        if len(people) % 2:
            extra_to_first = not extra_to_first
        cond[first] += people[:k]
        cond[second] += people[k:]
    if len(decliners) == 1:   # nobody to pair them with: they join the smaller condition's students
        smaller = min(cond, key=lambda c: len(cond[c]))
        cond[smaller].append(decliners[0])
        notes.append(f"{decliners[0].name} is the only student without consent, so they are matched with "
                     f"{smaller} students.")
        decliners = []

    def block(people):
        people = sorted(people, key=lambda s: s.key)
        if len(people) < 2:
            return [], [f"{people[0].name} has nobody to be matched with in their group."] if people else []
        half = len(people) // 2
        groups, block_notes = pair_sides(ctx, people[:half], people[half:])
        return [groups[m] for m in sorted(groups)], block_notes

    blocks = {c: block(cond[c]) for c in cond}
    declined, declined_notes = block(decliners)
    notes += blocks[first][1] + blocks[second][1] + declined_notes
    counts = {c: len(cond[c]) for c in cond}
    extra = {first: [], second: []}
    for people in declined:
        c = min(counts, key=lambda x: counts[x])
        extra[c].append(people)
        counts[c] += len(people)
    groups, conditions, n = {}, {}, 0
    for c in (first, second):
        for people in blocks[c][0] + extra[c]:
            n += 1
            groups[n] = people
            conditions[n] = c
    if decliners:
        notes.append(f"Students without consent are matched with each other: "
                     f"{', '.join(str(m) for m in groups if any(p.student in decliners for p in groups[m]))}.")
    return groups, conditions, notes


def condition_balance(ctx: Context, groups: dict, conditions: dict[int, str]) -> dict:
    """How many students of each gender are in each condition and role (research students only)."""
    out = {c: {r: {} for r in ctx.roles} for c in ctx.conditions}
    for m, people in groups.items():
        for p in people:
            gender, consent = ctx.baseline.get(p.key, ("", ""))
            if consent == "Yes" and m in conditions:
                bucket = out[conditions[m]][p.role]
                bucket[gender or "unknown"] = bucket.get(gender or "unknown", 0) + 1
    return out


def sides_from_previous(ctx: Context, ordered: list[ns.Student]) -> tuple[list, list, list[str]]:
    """Each student's side (first or second role) in the earlier simulation's draft, alphabetical within a side.
    Students who weren't in that draft go to the smaller side; if drops leave the sides more than one apart, the
    alphabetically last students of the bigger side move over."""
    code = ctx.sim.get("rotate_from")
    if code not in SETTINGS:
        raise ns.SkillError("draft_method_unknown", f"{ctx.sim['name']} has no earlier simulation set to rotate from.")
    prev = SETTINGS[code]
    tab = ns.read_sim_tab(ctx.wb, code, prev["roles"])
    if not tab.draft_members:
        raise ns.SkillError("previous_draft_missing", f"The {code} tab has no draft table, so each student's side "
                                                      f"from {prev['name']} isn't known.")
    side = {ctx.person_from_tab(m).key: prev["roles"].index(m.role) for m in tab.draft_members}
    sides = ([s for s in ordered if side.get(s.key) == 0], [s for s in ordered if side.get(s.key) == 1])
    notes = []
    for s in (s for s in ordered if s.key not in side):
        i = 0 if len(sides[0]) <= len(sides[1]) else 1
        sides[i].append(s)
        notes.append(f"{s.name} wasn't in the {code} draft and goes on the {ctx.roles[i].title()} side.")
    while abs(len(sides[0]) - len(sides[1])) > 1:
        big = 0 if len(sides[0]) > len(sides[1]) else 1
        moved = sides[big].pop()
        sides[1 - big].append(moved)
        notes.append(f"{moved.name} moves to the {ctx.roles[1 - big].title()} side to keep the sides even.")
    left, right = (sorted(x, key=lambda s: s.key) for x in sides)
    return left, right, notes


def pair_sides(ctx: Context, left: list[ns.Student], right: list[ns.Student]) -> tuple[dict[int, list[Person]], list[str]]:
    """Match the two sides in order. An extra student joins the last match, unless that would make someone "the 1"
    in a 1v2 for a second time or repeat a partner; then the nearest earlier match where neither happens."""
    first_role, second_role = ctx.roles
    n = min(len(left), len(right))
    groups = {i + 1: [Person(a.name, "", first_role, a, "exact"), Person(b.name, "", second_role, b, "exact")]
              for i, (a, b) in enumerate(zip(left[:n], right[:n]))}
    notes = []
    extras = [(s, first_role) for s in left[n:]] + [(s, second_role) for s in right[n:]]
    for student, role in extras:
        extra = Person(student.name, "", role, student, "exact")
        target = next((m for m in sorted(groups, reverse=True) if fits(ctx, groups[m], extra)), max(groups))
        if target != max(groups):
            last = groups[max(groups)]
            alone = solo_of(last + [extra], ctx.roles)
            met = [q.name for q in last if ctx.history.shared_ids(extra.key, q.key)]
            reasons = ([f"match {max(groups)} already has three students"] if len(last) >= MAX_GROUP else []) + \
                      ([f"{alone.name} would face two partners alone again"] if alone and ctx.solo.get(alone.key)
                       else []) + ([f"{extra.name} was already partners with {', '.join(met)}"] if met else [])
            notes.append(f"{extra.name} joins match {target} as a second {role.title()} instead of match "
                         f"{max(groups)}, because {' and '.join(reasons)}.")
        groups[target].append(extra)
    return groups, notes


def fits(ctx: Context, people: list[Person], newcomer: Person) -> bool:
    """Whether a student can join a match without a repeat partner or a second turn as "the 1" in a 1v2."""
    if len(people) + 1 > MAX_GROUP or any(ctx.history.shared_ids(newcomer.key, q.key) for q in people):
        return False
    alone = solo_of(people + [newcomer], ctx.roles)
    return not (alone and ctx.solo.get(alone.key))


def draft_rows(groups: dict[int, list[Person]], roles: list[str]) -> list[tuple[int | None, dict[str, Person | None]]]:
    rows = []
    for match, people in sorted(groups.items()):
        by_role = {r: [p for p in people if p.role == r] for r in roles}
        for k in range(max(len(v) for v in by_role.values())):
            rows.append((match if k == 0 else None, {r: (by_role[r][k] if k < len(by_role[r]) else None) for r in roles}))
    return rows


# ---------------------------------------------------------------- writing safely

def snapshot_values(wb) -> dict:
    return {(ws.title, c.coordinate): c.value for ws in wb.worksheets for row in ws.iter_rows() for c in row
            if c.value is not None}


def save_and_verify(ctx: Context, written: dict[tuple[str, str], object], label: str) -> Path:
    """Back up, save, and prove that only the intended cells changed."""
    before = snapshot_values(load_workbook(ctx.roster))
    backup = ns.backup(ctx.roster, label)
    ns.save_workbook(ctx.wb, ctx.roster)
    after = snapshot_values(load_workbook(ctx.roster))
    unexpected = [f"'{t}'!{c}" for (t, c) in set(before) | set(after)
                  if (t, c) not in written and before.get((t, c)) != after.get((t, c))]
    wrong = [f"'{t}'!{c}" for (t, c), v in written.items() if after.get((t, c)) != (v if v != "" else None)]
    if unexpected or wrong:
        import shutil
        shutil.copy2(backup, ctx.roster)
        raise ns.SkillError("write_verification_failed", "The workbook didn't save as intended, so the backup was "
                                                         "restored and nothing changed.",
                            {"unexpected_changes": unexpected[:20], "wrong_cells": wrong[:20]})
    return backup


def set_tracked(ws, written: dict, row: int, col: int, value) -> None:
    ns.set_cell(ws, row, col, value)
    written[(ws.title, ws.cell(row, col).coordinate)] = value


def roles_locked(ctx: Context) -> bool:
    log = ctx.roster.parent / ns.LOG_NAME
    if not log.exists():
        return False
    ws = load_workbook(log).active
    return any(ns.clean(r[1]) == f"H3 Role emails sent ({ctx.code})" for r in ws.iter_rows(min_row=2, values_only=True))


# ---------------------------------------------------------------- commands

def cmd_snapshot(args):
    ctx = Context(args)
    tab = ctx.tab
    ns.emit({
        "ok": True, "workbook": str(ctx.roster), "simulation": ctx.code, "class_tab": ctx.class_tab,
        "students": len(ctx.students), "missing_email": [s.name for s in ctx.students if not s.email],
        "class_list_warnings": ctx.class_warnings,
        "draft_table": {"matches": len(tab.groups(tab.draft_members)) if tab.draft_members else 0,
                        "rows_available": len(tab.draft_prefilled) + len({m.row for m in tab.draft_members})},
        "final_table": {"matches": len(tab.groups(tab.final_members)) if tab.final_members else 0,
                        "absent": [m.name for m in tab.absent],
                        "rows_available": tab.draft_header - tab.final_header - 1},
        "roles_locked": roles_locked(ctx),
        "earlier_simulations_found": sorted({i.split("_")[0] for ids in ctx.history.ids_by_student.values() for i in ids}),
        "history_names_not_linked": ctx.unlinked_history,
        "can_draft": ctx.sim.get("draft_method") in DRAFT_METHODS,
    })


def cmd_draft(args, write: bool = False):
    ctx = Context(args)
    groups, absent, notes, conditions = compute_draft(ctx, args)
    checks = check_groups(ctx, groups, absent, "draft")
    result = {"ok": True, "simulation": ctx.code, "matches": len(groups), "students": sum(map(len, groups.values())),
              "known_absent": [p.name for p in absent], "draft": table_preview(groups, ctx.roles, conditions),
              **({"condition_balance": condition_balance(ctx, groups, conditions)} if conditions else {}),
              "placement_notes": notes,
              **({"conditions_note": "Gender and consent aren't on the class list yet (baseline survey), so this "
                                     "draft has no experimental conditions."}
                 if ctx.sim.get("conditions") and not ctx.conditions else {}),
              "swaps_applied": args.swap, **checks}
    if not write:
        ctx.log("T2 Draft preview", f"{len(groups)} matches; absent: {[p.name for p in absent] or 'none'}; "
                                    f"swaps: {args.swap or 'none'}; {checks['summary']}.")
        ns.emit(result)
        return
    if checks["errors"]:
        raise ns.SkillError("draft_has_errors", "The draft has errors, so it wasn't written.", checks)
    if checks["warnings"] and not args.accept_warnings:
        raise ns.SkillError("warnings_not_accepted", "The draft has warnings. Confirm them with the instructor, then "
                                                     "run write-draft again with --accept-warnings.", checks)
    tab, ws = ctx.tab, ctx.wb[ctx.code]
    if tab.draft_members:
        if not args.replace:
            raise ns.SkillError("draft_exists", f"The {ctx.code} draft table already has names. Ask the instructor "
                                                "before replacing it, then use --replace.",
                                {"current_draft": table_preview(ctx.tab_groups(tab.draft_members), ctx.roles)})
        old_roles = {ctx.person_from_tab(m).key: m.role for m in tab.draft_members}
        changed = [p.name for ps in groups.values() for p in ps if p.key in old_roles and old_roles[p.key] != p.role]
        if changed and roles_locked(ctx) and not args.confirm_role_change:
            raise ns.SkillError("roles_locked", "Role emails have already gone out, and this draft changes roles for: "
                                                f"{', '.join(changed)}. Confirm with the instructor that she will "
                                                "re-send those packets, then add --confirm-role-change.",
                                {"role_changes": changed})
    rows = draft_rows(groups, ctx.roles)
    region = sorted(set(tab.draft_prefilled) | {m.row for m in tab.draft_members})
    first_row = tab.draft_header + 1
    if not region or len(rows) > len(region) or region != list(range(first_row, first_row + len(region))):
        raise ns.SkillError("tab_too_short", f"The {ctx.code} draft table needs {len(rows)} rows, but the prepared "
                                             f"tab has {len(region)} numbered rows under MATCH. Add match numbers to "
                                             "the tab and try again.")
    written: dict = {}
    cond_col = max(tab.draft_columns.values()) + 1 if conditions else None
    if cond_col:
        set_tracked(ws, written, tab.draft_header, cond_col, "CONDITION")
    for i, row in enumerate(region):
        if i < len(rows):
            match, by_role = rows[i]
            set_tracked(ws, written, row, tab.draft_match_column, match)
            for role, col in tab.draft_columns.items():
                set_tracked(ws, written, row, col, by_role[role].name if by_role[role] else None)
            if cond_col:
                set_tracked(ws, written, row, cond_col, conditions.get(match) if match is not None else None)
        else:  # unused prepared rows: clear names and the leftover match number, as on her own tabs
            for col in (tab.draft_match_column, *tab.draft_columns.values(), *([cond_col] if cond_col else [])):
                if ws.cell(row, col).value is not None:
                    set_tracked(ws, written, row, col, None)
    backup = save_and_verify(ctx, written, f"before {ctx.code} draft")
    result.update({"written_to": f"'{ctx.code}' draft table, rows {region[0]}-{region[len(rows) - 1]}",
                   "backup": str(backup)})
    warning = ctx.log("T4 Write draft", f"Draft written: {len(groups)} matches, rows {region[0]}-{region[len(rows) - 1]}. "
                                        f"Accepted warnings: {checks['warnings'] or 'none'}. Backup: {backup.name}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)


def cmd_check(args):
    ctx = Context(args)
    tab = ctx.tab
    if args.stage == "final":
        if not tab.final_members:
            raise ns.SkillError("no_final_table", f"The {ctx.code} final table is empty.")
        groups = ctx.tab_groups(tab.final_members)
        absent = [ctx.person_from_tab(m) for m in tab.absent]
        draft_roles = {ctx.person_from_tab(m).key: m.role for m in tab.draft_members} if tab.draft_members else None
    else:
        if not tab.draft_members:
            raise ns.SkillError("no_draft_table", f"The {ctx.code} draft table is empty.")
        groups, absent, draft_roles = ctx.tab_groups(tab.draft_members), [], None
    checks = check_groups(ctx, groups, absent, args.stage, draft_roles)
    ctx.log("T3 Check", f"{args.stage} table: {checks['summary']}.")
    ns.emit({"ok": True, "simulation": ctx.code, "stage": args.stage, "matches": len(groups),
             "table": table_preview(groups, ctx.roles), **checks})


def cmd_bcc(args):
    ctx = Context(args)
    tab = ctx.tab
    members = tab.final_members or tab.draft_members
    if not members:
        raise ns.SkillError("no_draft_table", f"The {ctx.code} draft table is empty. Write the draft first.")
    groups = ctx.tab_groups(members)
    conditions = draft_conditions(ctx)
    # Each student's condition is their draft match's (absence moves keep them within it).
    cond_of = {ctx.person_from_tab(m).key: c for match, ms in ctx.tab.groups(tab.draft_members).items()
               for m in ms for c in [conditions.get(match)] if c} if conditions else {}
    lists, missing = {}, []
    for role in ctx.roles:
        people = [p for ps in groups.values() for p in ps if p.role == role]
        missing += [p.name for p in people if not p.email]
        for label in (sorted(set(cond_of.values()), key=list(ctx.sim.get("conditions") or []).index)
                      if conditions else [None]):
            chosen = [p for p in people if label is None or cond_of.get(p.key) == label]
            emails = [p.email for p in chosen if p.email]
            lists[f"{role}-{label}" if label else role] = {"count": len(emails), "bcc": "; ".join(emails)}
    path = ctx.roster.parent / f"{ctx.code} role emails {date.today().isoformat()}.txt"
    text = "\n\n".join(f"{role} ({v['count']} students):\n{v['bcc']}" for role, v in lists.items())
    try:
        path.write_text(text + "\n", encoding="utf-8")
        saved = str(path)
    except PermissionError:
        saved = None
    counts = ", ".join(f"{role}: {v['count']}" for role, v in lists.items())
    ctx.log("T5 Role BCC lists", f"{counts}; missing email: {missing or 'none'}.")
    ns.emit({"ok": True, "simulation": ctx.code, "lists": lists, "missing_email": missing, "saved_to": saved})


def cmd_roles_sent(args):
    ctx = Context(args)
    ctx.log("H3 Role emails sent", "The instructor confirmed the role emails were sent. Roles are locked.")
    ns.emit({"ok": True, "simulation": ctx.code, "roles_locked": True})


def propose_final(ctx: Context, args):
    tab = ctx.tab
    if not tab.draft_members:
        raise ns.SkillError("no_draft_table", f"The {ctx.code} draft table is empty, so there is nothing to update.")
    groups = ctx.tab_groups(tab.draft_members)
    draft_roles = {p.key: p.role for ps in groups.values() for p in ps}
    everyone = [p for ps in groups.values() for p in ps]
    # Students on the class list but not in the draft were usually already known to be absent when drafting.
    off_draft = [Person(s.name, "", "", s, "exact") for s in ctx.students if s.key not in draft_roles]
    absent, extra_absent, problems = [], [], []
    for entry in args.absent:
        if not entry.strip():
            continue
        found, candidates, rule = match_entry(entry, everyone)
        if found:
            absent.append(found)
            continue
        if not candidates or rule == "none":
            other, _, _ = match_entry(entry, off_draft)
            if other:
                extra_absent.append(other)
                continue
        problems.append({"entry": entry, "reason": "more than one student fits" if candidates and rule != "none"
                         else "no student fits", "suggestions": [p.name for p in candidates]})
    if problems:
        raise ns.SkillError("absence_unclear", "Some absent students couldn't be matched to one student in the draft.",
                            {"unclear": problems})
    # A drafted student no longer on the class list dropped the class: absent this week, left off later tabs.
    # A name that is only "likely" a class-list student is still asked about, never treated as dropped.
    named = {p.key for p in absent}
    dropped = [p for p in everyone if p.link == "none"]
    absent += [p for p in dropped if p.key not in named]
    absent_keys = {p.key for p in absent}
    remaining = {m: [p for p in ps if p.key not in absent_keys] for m, ps in groups.items()}
    complete = {m for m, ps in remaining.items() if all(any(p.role == r for p in ps) for r in ctx.roles)}
    placements = {}
    for spec in args.place:
        name, _, match = spec.rpartition("=")
        student = ctx.by_name(name)
        if not match.strip().isdigit() or int(match) not in complete:
            raise ns.SkillError("bad_option", f"--place {spec}: match {match} isn't a match still in use.")
        placements[student.key] = int(match)
    final = {m: list(remaining[m]) for m in sorted(complete)}
    conds = draft_conditions(ctx)   # with experimental conditions, a stranded student stays in their condition
    same = (lambda a, b: conds.get(a) == conds.get(b)) if conds else (lambda a, b: True)
    moves, needs_placement, cross = [], [], []
    for m in sorted(set(remaining) - complete):
        stranded = remaining[m]
        if not stranded:
            continue
        gone = [p for p in groups[m] if p.key in absent_keys]
        lost = ", ".join(p.name for p in gone)
        why = ("is no longer on the class list" if all(p in dropped for p in gone) else "is absent")
        for p in stranded:
            if p.key in placements:
                target, how = placements[p.key], "placed by the instructor"
                if not same(target, m):
                    cross.append(f"{p.name} (condition {conds.get(m)}) was placed in match {target}, which is "
                                 f"condition {conds.get(target)}.")
            else:
                earlier = [x for x in final if x < m and same(x, m)]
                later = [x for x in final if x > m and same(x, m)]
                target = earlier[-1] if earlier else (later[0] if later else None)
                in_cond = f" in condition {conds[m]}" if conds.get(m) else ""
                how = (f"the match just before{in_cond}" if earlier
                       else f"the next match{in_cond}, since there is no earlier one")
                if target is None and conds:
                    needs_placement.append({"student": p.name, "from_match": m, "suggested_match": None,
                                            "reason": f"no other match in condition {conds.get(m)} is left"})
                    continue
                if target is None:
                    raise ns.SkillError("no_match_left", "No complete match is left to join.")
                too_big = len(final[target]) + 1 > MAX_GROUP
                repeat = any(ctx.history.shared_ids(p.key, q.key) for q in final[target])
                alone = solo_of(final[target] + [p], ctx.roles)
                solo_again = bool(alone and ctx.solo.get(alone.key))
                if too_big or repeat or solo_again:
                    reason = ("that match would have more than three students" if too_big
                              else "that match would repeat a partner from an earlier simulation" if repeat
                              else f"{alone.name} would face two partners alone again (already in "
                                   f"{', '.join(ctx.solo[alone.key])})")
                    needs_placement.append({"student": p.name, "from_match": m, "suggested_match": target,
                                            "reason": reason})
                    continue
            final[target].append(p)
            moves.append(f"{p.name} joins match {target} as a second {p.role.title()} because {lost} "
                         f"(match {m}) {why}; {how}.")
    all_absent = absent + extra_absent
    checks = check_groups(ctx, final, all_absent, "final", draft_roles)
    checks["warnings"] += cross
    if needs_placement:
        checks["errors"].append("Some stranded students need the instructor to choose a match.")
    return final, all_absent, dropped, moves, needs_placement, checks, draft_roles, conds


def cmd_absences(args, write: bool = False):
    ctx = Context(args)
    final, absent, dropped, moves, needs_placement, checks, _, conds = propose_final(ctx, args)
    result = {"ok": True, "simulation": ctx.code, "absent": [p.name for p in absent],
              "dropped": [p.name for p in dropped], "moves": moves,
              "needs_placement": needs_placement, "final": table_preview(final, ctx.roles, conds),
              "matches": len(final),
              **checks}
    if not write:
        ctx.log("T9 Absence proposal", f"Absent: {[p.name for p in absent] or 'none'}; "
                                       f"no longer on the class list: {[p.name for p in dropped] or 'none'}; "
                                       f"moves: {moves or 'none'}; "
                                       f"{checks['summary']}.")
        ns.emit(result)
        return
    if checks["errors"]:
        raise ns.SkillError("final_has_errors", "The final matches have errors, so they weren't written.", result)
    if checks["warnings"] and not args.accept_warnings:
        raise ns.SkillError("warnings_not_accepted", "The final matches have warnings. Confirm them with the "
                                                     "instructor, then add --accept-warnings.", checks)
    tab, ws = ctx.tab, ctx.wb[ctx.code]
    region = list(range(tab.final_header + 1, tab.draft_header))
    role_cols = {rc.role: rc for rc in tab.final_columns}
    table_cols = {tab.match_column} | {c for rc in tab.final_columns for c in
                                       (rc.name, rc.email, rc.current_id, *rc.prior_ids.values())}
    # With conditions, Gender (from the class list) and Intervention (the condition) are filled in too (Meeting 4).
    gender_cols, intervention_col = {}, None
    if conds:
        hr = tab.final_header
        gender_cols = {rc.role: rc.current_id + 1 for rc in tab.final_columns
                       if ns.normalize(ws.cell(hr, rc.current_id + 1).value) == "gender"}
        intervention_col = next((c for c in range(1, ws.max_column + 2)
                                 if ns.normalize(ws.cell(hr, c).value) == "intervention"), None)
        table_cols |= set(gender_cols.values()) | ({intervention_col} if intervention_col else set())
    cond_of = {p.key: conds[m] for m, ps in ctx.tab_groups(tab.draft_members).items() for p in ps if m in conds}
    # Columns beside the table that she fills herself (Gender, Intervention): never written, but checked.
    other_cols = [c for c in range(1, max(table_cols) + 3) if c not in table_cols]
    occupied = [ws.cell(r, c).coordinate for r in region for c in table_cols
                if ws.cell(r, c).value is not None and not (c == tab.match_column and isinstance(ws.cell(r, c).value, (int, float)))]
    other_filled = [ws.cell(r, c).coordinate for r in region for c in other_cols if ws.cell(r, c).value is not None]
    if (occupied or other_filled) and not args.replace:
        raise ns.SkillError("final_area_not_empty", f"The {ctx.code} final table already has entries. Ask the "
                                                    "instructor before replacing it, then use --replace.",
                            {"cells": (occupied + other_filled)[:20]})
    rows = draft_rows(final, ctx.roles)
    needed = len(rows) + (1 + len(absent) if absent else 0)
    if needed > len(region) - 1:
        raise ns.SkillError("tab_too_short", f"The {ctx.code} final table needs {needed} rows above the draft table "
                                             f"but only {len(region) - 1} are free.")
    written: dict = {}
    for row in region:
        for col in table_cols:
            if ws.cell(row, col).value is not None:
                set_tracked(ws, written, row, col, None)

    def write_person(row, p: Person, role: str, pair_id: str):
        rc = role_cols[role]
        if role in gender_cols:
            set_tracked(ws, written, row, gender_cols[role], (ctx.baseline or {}).get(p.key, ("", ""))[0] or None)
        if intervention_col and cond_of.get(p.key):
            set_tracked(ws, written, row, intervention_col, cond_of[p.key])
        set_tracked(ws, written, row, rc.name, p.name)
        set_tracked(ws, written, row, rc.email, p.email or (p.student.email if p.student else None))
        set_tracked(ws, written, row, rc.current_id, pair_id)
        for code, col in rc.prior_ids.items():
            ids = [i for i in ctx.history.ids_by_student.get(p.key, set()) if i.startswith(code + "_")]
            missed = code in ctx.history.absences_by_student.get(p.key, set())
            set_tracked(ws, written, row, col, ids[0] if ids else (f"{code}_0" if missed else None))

    r = region[0]
    current = None
    for match, by_role in rows:
        current = match if match is not None else current
        set_tracked(ws, written, r, tab.match_column, match)
        for role, p in by_role.items():
            if p:
                write_person(r, p, role, f"{ctx.code}_{current}")
        r += 1
    r += 1
    first_role = ctx.roles[0]
    for p in absent:  # under their own role's columns; students absent from the draft go under the first role
        write_person(r, p, p.role if p.role in role_cols else first_role, f"{ctx.code}_0")
        r += 1
    backup = save_and_verify(ctx, written, f"before {ctx.code} final")
    result.update({"written_to": f"'{ctx.code}' final table, rows {region[0]}-{r - 1}", "backup": str(backup)})
    if other_filled:
        result["note"] = ("Gender, Intervention, or other columns next to the final table had entries; they were left "
                          "untouched, so check they still line up with the right students.")
    warning = ctx.log("T9 Write final", f"Final matches written: {len(final)} matches; absent: "
                                        f"{[p.name for p in absent] or 'none'}; moves: {moves or 'none'}. "
                                        f"Backup: {backup.name}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)


def cmd_log(args):
    ctx = Context(args)
    warning = ctx.log(args.step, args.details)
    ns.emit({"ok": True, **({"log_warning": warning} if warning else {})})


# ---------------------------------------------------------------- baseline survey: gender and consent

BASELINE = {"consent": "Q1", "first": "Q11", "last": "Q14", "gender": "Q15", "gender_other": "Q15_4_TEXT"}
CONSENT = {"1": "Yes", "2": "No"}
GENDER = {"1": "M", "2": "F"}
NEW_COLUMNS = ["Gender", "Consent"]


def read_baseline(path: Path) -> list[dict]:
    """Responses from the Qualtrics baseline export (number codes): consent, names, gender."""
    if not path.exists():
        raise ns.SkillError("file_missing", f"Could not find the baseline survey export {path.name}.")
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    except PermissionError:
        raise ns.SkillError("file_locked", f"{path.name} is open in Excel. Close it and try again.")
    codes = [c.strip() for c in rows[0]] if rows else []
    missing = [c for c in BASELINE.values() if c not in codes]
    if missing:
        raise ns.SkillError("survey_layout", f"The baseline export has no {', '.join(missing)} column. The survey "
                                             "may have been edited.", {"columns": codes})
    skip = 2 if len(rows) > 2 and rows[2] and rows[2][0].startswith('{"ImportId') else 0
    col = {key: codes.index(code) for key, code in BASELINE.items()}
    status = codes.index("Status") if "Status" in codes else None
    rid = codes.index("ResponseId") if "ResponseId" in codes else None
    when = codes.index("RecordedDate") if "RecordedDate" in codes else None
    out = []
    for n, row in enumerate(rows[1 + skip:], start=1):
        row = row + [""] * (len(codes) - len(row))
        if status is not None and ns.clean(row[status]) not in ("", "0", "IP Address"):
            continue   # a survey preview or test
        values = {key: ns.clean(row[c]) for key, c in col.items()}
        if not (values["first"] or values["last"]):
            continue
        if not values["consent"].isdigit() and values["consent"]:   # exported as choice text
            raise ns.SkillError("survey_layout", "This baseline export has answer text instead of number codes. "
                                                 "Download it again from Qualtrics with 'Use numeric values'.")
        out.append({"rid": row[rid] if rid is not None and row[rid] else f"row {n}",
                    "time": row[when] if when is not None else "", **values})
    return out


def baseline_values(students: list[ns.Student], responses: list[dict], args) -> tuple[dict, dict]:
    """{student key: (gender, consent)} and a report. A student who chose Other is excluded from the research;
    one with no survey counts as declined (Meeting 4)."""
    by_name = {s.name: s for s in students}
    assigned = {}
    for spec in args.assign:
        rid, _, name = spec.partition("=")
        if name.strip() not in by_name or rid.strip() not in {r["rid"] for r in responses}:
            raise ns.SkillError("bad_decision", f"--assign {spec}: the response ID or the class-list name "
                                                "('Last, First') was not found.")
        assigned[rid.strip()] = by_name[name.strip()]
    claims: dict[str, list[dict]] = {}
    unresolved, decisions = [], []
    for r in responses:
        if r["rid"] in args.leave_out:
            decisions.append(f"Left out response {r['rid']} ({r['first']} {r['last']})")
            continue
        if r["rid"] in assigned:
            student = assigned[r["rid"]]
            decisions.append(f"Response {r['rid']} ({r['first']} {r['last']}) is {student.name}")
        else:
            res = ns.resolve_student(r["first"], r["last"], students)
            if not res.confident:
                unresolved.append({"response": r["rid"], "typed_name": f"{r['first']} {r['last']}".strip(),
                                   "reason": "the last name matches but the first name doesn't" if res.how == "likely"
                                   else "more than one student could match" if len(res.candidates) > 1
                                   else "close to a student's name, but not the same" if res.candidates
                                   else "no student on the class list matches (dropped the class?)",
                                   "suggestions": [c.name for c in (res.candidates or [res.student]) if c][:3]})
                continue
            student = res.student
        claims.setdefault(student.key, []).append(r)
    values, report = {}, {"declined": [], "excluded": [], "no_survey": [], "duplicates": []}
    for s in students:
        rs = sorted(claims.get(s.key, []), key=lambda r: r["time"])
        if not rs:
            values[s.key] = ("", "No (no survey)")
            report["no_survey"].append(s.name)
            continue
        if len(rs) > 1:
            report["duplicates"].append(f"{s.name} took the survey {len(rs)} times; the latest is used.")
        r = rs[-1]
        gender = GENDER.get(r["gender"], "Other" if r["gender"] else "")
        consent = CONSENT.get(r["consent"], "No")
        if gender == "Other":
            consent = "Excluded"
            report["excluded"].append(s.name)
        elif consent == "No":
            report["declined"].append(s.name)
        values[s.key] = (gender, consent)
    report["gender_blank"] = [s.name for s in students if values[s.key][0] == "" and s.name not in report["no_survey"]]
    return values, {"unresolved": unresolved, "decisions": decisions, **report}


def insert_blockers(wb, ws, after_col: int) -> list[str]:
    """Things openpyxl would not move when columns are inserted, so inserting could break her tab."""
    issues = []
    if any(isinstance(c.value, str) and c.value.startswith("=") for row in ws.iter_rows() for c in row):
        issues.append(f"'{ws.title}' has formulas")
    if any(r.max_col > after_col for r in ws.merged_cells.ranges):
        issues.append(f"'{ws.title}' has merged cells to the right of Email")
    if len(ws.conditional_formatting):
        issues.append(f"'{ws.title}' has conditional formatting")
    if ws.data_validations.dataValidation:
        issues.append(f"'{ws.title}' has drop-down lists or data validation")
    if ws.tables:
        issues.append(f"'{ws.title}' has an Excel table")
    names = [ws.title, f"'{ws.title}'"]
    for other in wb.worksheets:
        if other is ws:
            continue
        if any(isinstance(c.value, str) and c.value.startswith("=") and any(n + "!" in c.value for n in names)
               for row in other.iter_rows() for c in row):
            issues.append(f"formulas on '{other.title}' refer to '{ws.title}'")
    if any(ws.title in str(getattr(d, "attr_text", "") or getattr(d, "value", "")) for d in
           (wb.defined_names.values() if hasattr(wb.defined_names, "values") else wb.defined_names.definedName)):
        issues.append(f"named ranges refer to '{ws.title}'")
    return issues


def cmd_baseline(args, write: bool = False):
    roster = Path(args.roster).expanduser().resolve()
    wb = ns.open_workbook(roster)
    tab, students, warnings = ns.read_class_list(wb)
    responses = read_baseline(Path(args.csv).expanduser().resolve())
    values, report = baseline_values(students, responses, args)
    counts = {"M": 0, "F": 0, "Other": 0, "Yes": 0, "No": 0, "Excluded": 0, "No (no survey)": 0}
    for gender, consent in values.values():
        counts[gender] = counts.get(gender, 0) + 1
        counts[consent] += 1
    result = {"ok": True, "class_tab": tab, "students": len(students), "responses": len(responses),
              "gender": {k: counts[k] for k in ("M", "F", "Other")},
              "consent": {k: counts[k] for k in ("Yes", "No", "Excluded", "No (no survey)")},
              **report, "class_list_warnings": warnings,
              "table": [{"student": s.name, "gender": values[s.key][0], "consent": values[s.key][1]} for s in students]}
    if not write:
        ns.write_log(roster.parent, "Baseline survey preview",
                     f"{len(responses)} responses for {len(students)} students; {len(report['unresolved'])} unresolved.")
        ns.emit(result)
        return
    if report["unresolved"]:
        raise ns.SkillError("unresolved_responses", "Some baseline responses need the instructor's decision first.",
                            {"unresolved": report["unresolved"]})
    ws = wb[tab]
    hr, headers = ns.find_header_row(ws, ["student name", "email"])
    email_col = next(c for h, c in headers.items() if "email" in h)
    present = [ns.normalize(ws.cell(hr, email_col + i).value) for i in (1, 2)]
    insert = present != [h.lower() for h in NEW_COLUMNS]
    if insert and any(h in ns.normalize(ws.cell(hr, c).value) for c in range(1, ws.max_column + 1)
                      for h in ("gender", "consent")):
        raise ns.SkillError("class_tab_layout", f"'{tab}' already has a Gender or Consent column, but not as the two "
                                                "columns just after Email. Ask her where they should be.")
    if insert:
        blockers = insert_blockers(wb, ws, email_col)
        if blockers:
            raise ns.SkillError("insert_columns_needed",
                                f"Adding two columns after Email on '{tab}' could break it ({'; '.join(blockers)}). "
                                f"Ask her to insert two blank columns just after Email, headed Gender and Consent, "
                                "then run this again; Claude will fill them in.", {"reasons": blockers})
    else:
        old = {s.key: (ns.clean(ws.cell(s.row, email_col + 1).value), ns.clean(ws.cell(s.row, email_col + 2).value))
               for s in students}
        changed = [f"{s.name}: {old[s.key]} -> {values[s.key]}" for s in students
                   if any(old[s.key]) and old[s.key] != values[s.key]]
        if changed and not args.replace:
            raise ns.SkillError("baseline_exists", "Gender and Consent are already filled in, and this would change "
                                                   "some of them. Ask her before using --replace.",
                                {"changes": changed[:20]})
    before = snapshot_values(load_workbook(roster))
    backup = ns.backup(roster, "before baseline")
    if insert:
        widths = {c: ws.column_dimensions[get_column_letter(c)].width for c in range(email_col + 1, ws.max_column + 1)
                  if get_column_letter(c) in ws.column_dimensions}
        ws.insert_cols(email_col + 1, 2)
        for c, width in sorted(widths.items(), reverse=True):
            ws.column_dimensions[get_column_letter(c + 2)].width = width
        for i, header in enumerate(NEW_COLUMNS, start=1):
            ws.column_dimensions[get_column_letter(email_col + i)].width = 10
            cell = ws.cell(hr, email_col + i)
            cell.value = header
            cell.font = copy(ws.cell(hr, email_col).font)
    written = {(tab, ws.cell(hr, email_col + i).coordinate): h for i, h in enumerate(NEW_COLUMNS, start=1)}
    for s in students:
        for i, value in enumerate(values[s.key], start=1):
            ns.set_cell(ws, s.row, email_col + i, value or None)
            written[(tab, ws.cell(s.row, email_col + i).coordinate)] = value or None
    ns.save_workbook(wb, roster)
    after = snapshot_values(load_workbook(roster))

    def moved(key):   # where a cell from before should be now
        t, coord = key
        if t != tab or not insert:
            return key
        c = ws.cell(1, 1).parent[coord]
        return (t, f"{get_column_letter(c.column + 2)}{c.row}") if c.column > email_col else key

    from openpyxl.utils.cell import coordinate_from_string, column_index_from_string
    wrong = []
    for key, value in before.items():
        letters, row = coordinate_from_string(key[1])
        col = column_index_from_string(letters)
        target = (key[0], f"{get_column_letter(col + 2)}{row}") if insert and key[0] == tab and col > email_col else key
        if target in written:
            continue
        if after.get(target) != value:
            wrong.append(f"'{target[0]}'!{target[1]}")
    wrong += [f"'{t}'!{c}" for (t, c), v in written.items() if after.get((t, c)) != v]
    expected_keys = {(k[0], f"{get_column_letter(column_index_from_string(coordinate_from_string(k[1])[0]) + 2)}"
                             f"{coordinate_from_string(k[1])[1]}")
                     if insert and k[0] == tab and column_index_from_string(coordinate_from_string(k[1])[0]) > email_col
                     else k for k in before} | set(written)
    wrong += [f"'{t}'!{c}" for (t, c) in after if (t, c) not in expected_keys]
    if wrong:
        import shutil
        shutil.copy2(backup, roster)
        raise ns.SkillError("write_verification_failed", "The workbook didn't save as intended, so the backup was "
                                                         "restored and nothing changed.", {"cells": wrong[:20]})
    result.update({"written_to": f"'{tab}', columns {get_column_letter(email_col + 1)}-"
                                 f"{get_column_letter(email_col + 2)}" + (" (inserted after Email; the columns to the "
                                                                          "right moved over by two)" if insert else ""),
                   "backup": str(backup)})
    warning = ns.write_log(roster.parent, "Baseline survey written",
                           f"Gender and Consent for {len(students)} students on '{tab}'"
                           f"{' (two columns inserted after Email)' if insert else ''}. Declined: "
                           f"{report['declined'] or 'none'}; excluded: {report['excluded'] or 'none'}; no survey: "
                           f"{report['no_survey'] or 'none'}. Backup: {backup.name}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    def add(name):
        sp = sub.add_parser(name)
        sp.add_argument("--roster", required=True, help="The instructor's roster workbook (.xlsx)")
        sp.add_argument("--simulation", default="UC", help="Simulation code (default UC)")
        sp.add_argument("--same-person", action="append", default=[],
                        help="'Tab Name=Class Name' when she confirms a tab name is a class-list student")
        return sp

    add("snapshot").set_defaults(func=cmd_snapshot)
    for name, write in (("draft", False), ("write-draft", True)):
        sp = add(name)
        sp.add_argument("--absent", action="append", default=[], help="A student already known to be absent")
        sp.add_argument("--swap", action="append", default=[], help="'Last, First;Last, First' to swap two students")
        if write:
            sp.add_argument("--accept-warnings", action="store_true")
            sp.add_argument("--replace", action="store_true", help="Replace a draft table that already has names")
            sp.add_argument("--confirm-role-change", action="store_true")
        sp.set_defaults(func=lambda a, w=write: cmd_draft(a, w))
    sp = add("check")
    sp.add_argument("--stage", choices=["draft", "final"], default="draft")
    sp.set_defaults(func=cmd_check)
    add("bcc").set_defaults(func=cmd_bcc)
    add("roles-sent").set_defaults(func=cmd_roles_sent)
    for name, write in (("absences", False), ("write-final", True)):
        sp = add(name)
        sp.add_argument("--absent", action="append", default=[], help="An absent student, as she named them")
        sp.add_argument("--place", action="append", default=[], help="'Last, First=MATCH' to place a stranded student")
        if write:
            sp.add_argument("--accept-warnings", action="store_true")
            sp.add_argument("--replace", action="store_true", help="Replace a final table that already has entries")
        sp.set_defaults(func=lambda a, w=write: cmd_absences(a, w))
    for name, write in (("baseline", False), ("write-baseline", True)):
        sp = sub.add_parser(name)
        sp.add_argument("--roster", required=True, help="The instructor's roster workbook (.xlsx)")
        sp.add_argument("--csv", required=True, help="The Week 1 baseline survey export (.csv, number codes)")
        sp.add_argument("--assign", action="append", default=[], help="RESPONSE_ID=Last, First (her decision)")
        sp.add_argument("--leave-out", action="append", default=[], help="Response ID to ignore")
        if write:
            sp.add_argument("--replace", action="store_true", help="Change Gender/Consent values already filled in")
        sp.set_defaults(func=lambda a, w=write: cmd_baseline(a, w))
    sp = add("log")
    sp.add_argument("--step", required=True)
    sp.add_argument("--details", required=True)
    sp.set_defaults(func=cmd_log)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    ns.run_cli(main)
