"""Check that opening and saving a workbook with openpyxl loses nothing.

The skills write into the instructor's own roster workbook, which also holds
exams, grades, and attendance. Before trusting that, run this on a copy of her
current workbook:

    python roundtrip_check.py "<path to workbook>.xlsx"

It saves a round-tripped copy next to a temporary folder (the original is
never modified) and compares, sheet by sheet: values and formulas, number
formats, fonts, fills, borders, alignment, column widths, row heights, merged
cells, freeze panes, comments, data validations, conditional formatting, sheet
order and visibility. It also lists any parts of the .xlsx package that
disappeared or changed size a lot. Exit code 0 means nothing was lost.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from openpyxl import load_workbook


def style_key(c):
    f, fl, b, a = c.font, c.fill, c.border, c.alignment
    return (
        c.number_format,
        (f.name, f.sz, f.b, f.i, f.u, f.strike, f.color.rgb if f.color is not None else None),
        (fl.fill_type, fl.fgColor.rgb if fl.fgColor is not None else None,
         getattr(fl.fgColor, "theme", None), getattr(fl.fgColor, "tint", None)),
        tuple((getattr(b, side).style if getattr(b, side) is not None else None)
              for side in ("left", "right", "top", "bottom")),
        (a.horizontal, a.vertical, a.wrap_text, a.indent, a.text_rotation),
        c.protection.locked,
    )


def snapshot(path: Path) -> dict:
    wb = load_workbook(path)
    out = {"order": [(ws.title, ws.sheet_state) for ws in wb.worksheets], "sheets": {}}
    for ws in wb.worksheets:
        cells = {}
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None or c.has_style:
                    cells[c.coordinate] = (c.value, style_key(c),
                                           (c.comment.text, c.comment.author) if c.comment else None)
        out["sheets"][ws.title] = {
            "cells": cells,
            "widths": {k: round(v.width or 0, 2) for k, v in ws.column_dimensions.items()},
            "hidden_cols": sorted(k for k, v in ws.column_dimensions.items() if v.hidden),
            "heights": {k: round(v.height or 0, 2) for k, v in ws.row_dimensions.items() if v.height},
            "merged": sorted(str(r) for r in ws.merged_cells.ranges),
            "freeze": ws.freeze_panes,
            "validations": sorted((str(dv.sqref), dv.type, dv.formula1) for dv in ws.data_validations.dataValidation),
            "condfmt": sorted(str(r.sqref) for r in ws.conditional_formatting),
            "autofilter": ws.auto_filter.ref,
            "print_area": str(ws.print_area) if ws.print_area else None,
            "page_setup": (ws.page_setup.orientation, ws.page_setup.paperSize, ws.page_setup.scale,
                           ws.page_setup.fitToWidth, ws.page_setup.fitToHeight, ws.print_options.gridLines,
                           ws.page_margins.left, ws.page_margins.right, ws.page_margins.top,
                           ws.page_margins.bottom, ws.print_title_rows),
        }
    return out


# Parts openpyxl drops or renames that carry nothing the instructor would miss.
EXPECTED_PART_CHANGES = {
    "xl/calcChain.xml": "Excel's formula calculation order; rebuilt automatically on open",
    "xl/sharedStrings.xml": "text storage; openpyxl stores the same text differently",
    "docProps/app.xml": "file metadata; rebuilt on save",
}
EXPECTED_PREFIXES = {
    "xl/printerSettings/": "printer-driver settings (orientation and margins are kept and compared above)",
    "xl/worksheets/_rels/": "links to the printer settings and comments parts",
    "xl/comments": "comment storage, renamed; comment text and authors are compared above",
    "xl/drawings/vmlDrawing": "comment box drawing, rebuilt (boxes may reopen at default size)",
    "xl/drawings/commentsDrawing": "comment box drawing, rebuilt (boxes may reopen at default size)",
}


def explain(part: str) -> str | None:
    if part in EXPECTED_PART_CHANGES:
        return EXPECTED_PART_CHANGES[part]
    return next((why for prefix, why in EXPECTED_PREFIXES.items() if part.startswith(prefix)), None)


def package_parts(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        return {i.filename: i.file_size for i in z.infolist()}


def compare(a: dict, b: dict) -> list[str]:
    problems = []
    if a["order"] != b["order"]:
        problems.append(f"Sheet order or visibility changed: {a['order']} -> {b['order']}")
    for name, sa in a["sheets"].items():
        sb = b["sheets"].get(name)
        if sb is None:
            problems.append(f"Sheet '{name}' disappeared")
            continue
        for coord in sorted(set(sa["cells"]) | set(sb["cells"])):
            va, vb = sa["cells"].get(coord), sb["cells"].get(coord)
            if va != vb:
                problems.append(f"'{name}'!{coord}: {va} -> {vb}")
        for key in ("widths", "hidden_cols", "heights", "merged", "freeze", "validations", "condfmt",
                    "autofilter", "print_area", "page_setup"):
            if sa[key] != sb[key]:
                problems.append(f"'{name}' {key} changed: {sa[key]} -> {sb[key]}")
    return problems


def main():
    original = Path(sys.argv[1])
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "original.xlsx"
        out = Path(tmp) / "roundtrip.xlsx"
        shutil.copy2(original, src)
        load_workbook(src).save(out)
        problems = compare(snapshot(src), snapshot(out))
        pa, pb = package_parts(src), package_parts(out)
        missing = sorted(set(pa) - set(pb))
        added = sorted(set(pb) - set(pa))
        shrunk = sorted(p for p in set(pa) & set(pb) if pb[p] < 0.5 * pa[p] and pa[p] > 500)
        sheets = len(snapshot(src)["sheets"])
    print(f"Workbook: {original.name} ({sheets} sheets)")
    print(f"Cell, style, and sheet-setting differences: {len(problems)}")
    for p in problems[:40]:
        print("  ", p)
    if len(problems) > 40:
        print(f"   ... and {len(problems) - 40} more")
    unexpected = []
    for label, parts in (("missing after save", missing), ("added by save", added), ("much smaller after save", shrunk)):
        for part in parts:
            why = explain(part)
            if why:
                print(f"   expected: {part} {label} ({why})")
            else:
                unexpected.append(f"{part} {label}")
    print(f"Unexpected package changes: {unexpected or 'none'}")
    print("Note: formula results are not cached after saving; Excel recalculates them when the file is opened.")
    lost = problems or unexpected
    print("RESULT:", "differences found, review above" if lost else "nothing lost")
    sys.exit(1 if lost else 0)


if __name__ == "__main__":
    main()
