#!/usr/bin/env python3
"""Generate AXA UPN-Wechsel Kurzanleitung DOCX."""

from docx import Document
from docx.shared import Cm, Pt, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy
import os

# ── colours ──────────────────────────────────────────────────────────────────
C_BLUE   = "00008F"
C_RED    = "FF1721"
C_DARK   = "343C3D"
C_SECTBG = "EEEEF8"
C_WARNBG = "FFF0F0"
C_WARNTX = "8F0000"
C_GREYBG = "F5F5F5"
C_WHITE  = "FFFFFF"
C_BRDGRY = "CCCCCC"
C_BRDBLU = "BBBBE8"
C_HINT   = "8C9BA5"
C_SUBTTL = "9999CC"

IMG_PATH = "/root/.claude/uploads/cb3da536-4c85-53a7-8105-b6b8a4960349/bf765434-IMG_4052.png"
OUT_PATH = "/home/user/Claude/UPN_Wechsel_AXA.docx"

# ── helpers ───────────────────────────────────────────────────────────────────

def bg(cell, hex6):
    """Set cell background shading."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex6)
    # Remove existing shd if any
    for existing in tcPr.findall(qn('w:shd')):
        tcPr.remove(existing)
    tcPr.append(shd)


def _get_or_add_tblPr(table):
    """Get or add tblPr element on a table."""
    tbl = table._tbl
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    return tblPr


def _set_tbl_borders(tblPr, border_specs):
    """Set table borders. border_specs is a dict of side -> (val, color, sz) or None."""
    # Remove existing tblBorders
    for existing in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(existing)
    tblBorders = OxmlElement('w:tblBorders')
    for side, spec in border_specs.items():
        brd = OxmlElement(f'w:{side}')
        if spec is None:
            brd.set(qn('w:val'), 'none')
            brd.set(qn('w:sz'), '0')
            brd.set(qn('w:space'), '0')
            brd.set(qn('w:color'), 'auto')
        else:
            val, color, sz = spec
            brd.set(qn('w:val'), val)
            brd.set(qn('w:sz'), str(sz))
            brd.set(qn('w:space'), '0')
            brd.set(qn('w:color'), color)
        tblBorders.append(brd)
    tblPr.append(tblBorders)


def no_brd(table):
    """Remove all table borders."""
    tblPr = _get_or_add_tblPr(table)
    sides = ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']
    _set_tbl_borders(tblPr, {s: None for s in sides})


def box_brd(table, color_hex, sz=4):
    """Outer border only, no inside borders."""
    tblPr = _get_or_add_tblPr(table)
    outer_spec = ('single', color_hex, sz)
    none_spec = None
    sides = {
        'top': outer_spec,
        'left': outer_spec,
        'bottom': outer_spec,
        'right': outer_spec,
        'insideH': none_spec,
        'insideV': none_spec,
    }
    _set_tbl_borders(tblPr, sides)


def cmar(cell, top, bot, left, right):
    """Set cell margins in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    for existing in tcPr.findall(qn('w:tcMar')):
        tcPr.remove(existing)
    tcMar = OxmlElement('w:tcMar')
    for side, val in [('top', top), ('bottom', bot), ('left', left), ('right', right)]:
        m = OxmlElement(f'w:{side}')
        m.set(qn('w:w'), str(val))
        m.set(qn('w:type'), 'dxa')
        tcMar.append(m)
    tcPr.append(tcMar)


def valign(cell, v):
    """Set vertical alignment."""
    tcPr = cell._tc.get_or_add_tcPr()
    for existing in tcPr.findall(qn('w:vAlign')):
        tcPr.remove(existing)
    va = OxmlElement('w:vAlign')
    va.set(qn('w:val'), v)
    tcPr.append(va)


def fmt(p, align=None, sb=0, sa=0, li=None):
    """Format paragraph spacing/indent/alignment."""
    pf = p.paragraph_format
    if align is not None:
        p.alignment = align
    pf.space_before = Pt(sb)
    pf.space_after = Pt(sa)
    if li is not None:
        pf.left_indent = li
    # suppress line spacing
    pf.line_spacing = Pt(12)


def run(p, text, bold=False, italic=False, sz=9, col=None):
    """Add a run with Arial font."""
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.name = 'Arial'
    r.font.size = Pt(sz)
    if col:
        r.font.color.rgb = RGBColor.from_string(col)
    return r


def gap(doc, pt=4):
    """Add a minimal-height spacer paragraph."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = Pt(pt)
    r = p.add_run('')
    r.font.size = Pt(pt)
    r.font.name = 'Arial'


def add_table(doc, rows, cols, widths=None):
    """Add a table with no auto-spacing and optional column widths."""
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    # Set column widths
    if widths:
        for i, w in enumerate(widths):
            for row in table.rows:
                row.cells[i].width = w
    # Remove default table style spacing
    table.style = doc.styles['Table Grid']
    return table


def set_para_shading(para, fill_hex):
    """Set paragraph background shading."""
    pPr = para._p.get_or_add_pPr()
    for existing in pPr.findall(qn('w:shd')):
        pPr.remove(existing)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    pPr.append(shd)


def set_para_left_border(para, color_hex, sz=12):
    """Add a left border to a paragraph (for warning bar effect)."""
    pPr = para._p.get_or_add_pPr()
    for existing in pPr.findall(qn('w:pBdr')):
        pPr.remove(existing)
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), str(sz))
    left.set(qn('w:space'), '4')
    left.set(qn('w:color'), color_hex)
    pBdr.append(left)
    pPr.append(pBdr)


def set_row_height(row, height_twips):
    """Set exact row height in twips."""
    tr = row._tr
    trPr = tr.find(qn('w:trPr'))
    if trPr is None:
        trPr = OxmlElement('w:trPr')
        tr.insert(0, trPr)
    for existing in trPr.findall(qn('w:trHeight')):
        trPr.remove(existing)
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(height_twips))
    trHeight.set(qn('w:hRule'), 'exact')
    trPr.append(trHeight)


def set_col_width(table, col_idx, width):
    """Set column width for all cells in a column."""
    for row in table.rows:
        cell = row.cells[col_idx]
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        for existing in tcPr.findall(qn('w:tcW')):
            tcPr.remove(existing)
        tcW = OxmlElement('w:tcW')
        tcW.set(qn('w:w'), str(int(width.twips)))
        tcW.set(qn('w:type'), 'dxa')
        tcPr.append(tcW)


# ── document setup ────────────────────────────────────────────────────────────

doc = Document()

# Page margins
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(1.0)
section.bottom_margin = Cm(1.0)
section.left_margin = Cm(1.2)
section.right_margin = Cm(1.2)

# Default paragraph style
style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(9)
pf = style.paragraph_format
pf.space_before = Pt(0)
pf.space_after = Pt(0)

# ── 1. HEADER TABLE ───────────────────────────────────────────────────────────

hdr_table = add_table(doc, 1, 2, widths=[Cm(15), Cm(3.6)])
no_brd(hdr_table)

# Left cell
lc = hdr_table.rows[0].cells[0]
lc.width = Cm(15)
bg(lc, C_BLUE)
cmar(lc, 80, 80, 170, 60)
valign(lc, 'center')

# Para 1: AXA | title
p1 = lc.paragraphs[0]
fmt(p1, align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=0)
run(p1, 'AXA', bold=True, sz=18, col=C_WHITE)
run(p1, '  |  ', bold=False, sz=14, col=C_WHITE)
run(p1, 'UPN-Wechsel — Kurzanleitung', bold=True, sz=14, col=C_WHITE)

# Para 2: subtitle
p2 = lc.add_paragraph()
fmt(p2, align=WD_ALIGN_PARAGRAPH.LEFT, sb=2, sa=0)
run(p2, 'Was nach der Änderung deiner geschäftlichen E-Mail-Adresse zu tun ist',
    bold=False, sz=8.5, col=C_SUBTTL)

# Right cell: logo badge
rc = hdr_table.rows[0].cells[1]
rc.width = Cm(3.6)
bg(rc, C_BLUE)
cmar(rc, 80, 80, 60, 120)
valign(rc, 'center')

p_logo = rc.paragraphs[0]
fmt(p_logo, align=WD_ALIGN_PARAGRAPH.RIGHT, sb=0, sa=0)
run(p_logo, 'AXA', bold=True, sz=20, col=C_WHITE)

# ── 2. RED ACCENT BAR ────────────────────────────────────────────────────────

bar_table = add_table(doc, 1, 1)
no_brd(bar_table)
bar_cell = bar_table.rows[0].cells[0]
bg(bar_cell, C_RED)
set_row_height(bar_table.rows[0], 75)
cmar(bar_cell, 0, 0, 0, 0)
# Empty paragraph in bar
bp = bar_cell.paragraphs[0]
fmt(bp, sb=0, sa=0)
run(bp, '', sz=2)

# ── 3. Gap ───────────────────────────────────────────────────────────────────
gap(doc, 3)

# ── 4. INTRO TABLE ───────────────────────────────────────────────────────────

intro_table = add_table(doc, 1, 1)
box_brd(intro_table, C_BRDGRY, sz=4)
intro_cell = intro_table.rows[0].cells[0]
bg(intro_cell, C_GREYBG)
cmar(intro_cell, 100, 100, 120, 120)

ip = intro_cell.paragraphs[0]
fmt(ip, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=0)
run(ip, 'Dein ', sz=8.5, col=C_DARK)
run(ip, 'User Principal Name (UPN)', bold=True, sz=8.5, col=C_DARK)
run(ip, ' — deine geschäftliche E-Mail-Adresse — wurde geändert. '
    'Einige Microsoft-365-Apps müssen manuell neu verknüpft werden. '
    'Folge den Schritten — es dauert nur wenige Minuten.',
    sz=8.5, col=C_DARK)

# ── 5. Gap ───────────────────────────────────────────────────────────────────
gap(doc, 4)

# ── 6. SECTION 1 HEADER ──────────────────────────────────────────────────────

s1h_table = add_table(doc, 1, 1)
no_brd(s1h_table)
s1h_cell = s1h_table.rows[0].cells[0]
bg(s1h_cell, C_BLUE)
cmar(s1h_cell, 80, 80, 120, 120)

s1h_p = s1h_cell.paragraphs[0]
fmt(s1h_p, align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=0)
run(s1h_p, '1 — Microsoft OneNote — Notizbücher neu verknüpfen',
    bold=True, sz=10.5, col=C_WHITE)

# ── 7. SECTION 1 BODY ────────────────────────────────────────────────────────

s1b_table = add_table(doc, 1, 2, widths=[Cm(11.0), Cm(7.6)])
box_brd(s1b_table, C_BRDBLU, sz=4)

# Left col
lc1 = s1b_table.rows[0].cells[0]
lc1.width = Cm(11.0)
bg(lc1, C_SECTBG)
cmar(lc1, 100, 100, 120, 80)

# Steps for section 1
steps1 = [
    ('⚠', 'Vor dem Schließen: Sync-Fehler prüfen',
     'Sicherstellen, dass keine Sync-Fehler vorhanden sind. '
     'Falls ja: betroffene Notizbücher zuerst manuell aus dem lokalen Ordner sichern.',
     C_RED, True),
    ('1', 'Alle Notizbücher schließen',
     'Rechtsklick auf jedes Notizbuch im linken Bereich → Notizbuch schließen '
     '(Close This Notebook). Für alle wiederholen, dann App beenden.',
     C_BLUE, False),
    ('2', 'Bei OneDrive Web mit neuer Adresse anmelden',
     'Browser öffnen → onedrive.com → mit der neuen geschäftlichen '
     'E-Mail-Adresse (neuem UPN) anmelden.',
     C_BLUE, False),
    ('3', 'Notizbuch direkt aus OneDrive Web öffnen',
     'Zum Ordner des Notizbuchs navigieren und darauf klicken: öffnet sich in OneNote '
     'für das Web. (Erzwingt die Neuverknüpfung mit dem neuen UPN.)',
     C_BLUE, False),
    ('4', 'In der Desktop-App weiterarbeiten',
     'In OneNote für das Web oben rechts auf «In OneNote öffnen» klicken. '
     'Das Notizbuch ist nun korrekt mit dem neuen Konto verknüpft.',
     C_BLUE, False),
]

first_para = True
for num, label, desc, num_col, is_warning in steps1:
    # Label paragraph
    if first_para:
        lp = lc1.paragraphs[0]
        first_para = False
    else:
        lp = lc1.add_paragraph()
    fmt(lp, align=WD_ALIGN_PARAGRAPH.LEFT, sb=4, sa=0)
    run(lp, num + '  ', bold=True, sz=12, col=num_col)
    run(lp, label, bold=True, sz=9, col=C_DARK)

    # Description paragraph
    dp = lc1.add_paragraph()
    fmt(dp, align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=2, li=Cm(0.6))
    desc_col = C_RED if is_warning else C_DARK
    run(dp, desc, sz=8, col=desc_col)

# Right col: image + caption
rc1 = s1b_table.rows[0].cells[1]
rc1.width = Cm(7.6)
bg(rc1, C_SECTBG)
cmar(rc1, 100, 100, 80, 80)
valign(rc1, 'center')

img_p = rc1.paragraphs[0]
fmt(img_p, align=WD_ALIGN_PARAGRAPH.CENTER, sb=0, sa=4)

# Add image with proportional sizing
img_width = Cm(7.6) - Cm(1.3)  # ~Cm(6.3)
img_ratio = 351 / 345
img_height = img_width * img_ratio

if os.path.exists(IMG_PATH):
    img_run = img_p.add_run()
    img_run.add_picture(IMG_PATH, width=img_width, height=img_height)
else:
    run(img_p, '[Bild nicht gefunden]', sz=8, col=C_HINT)

# Caption
cap_p = rc1.add_paragraph()
fmt(cap_p, align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=0)
run(cap_p, 'Rechtsklick → Notizbuch schließen', italic=True, sz=7.5, col=C_HINT)

# ── 8. Gap ───────────────────────────────────────────────────────────────────
gap(doc, 4)

# ── 9. SECTION 2 HEADER ──────────────────────────────────────────────────────

s2h_table = add_table(doc, 1, 1)
no_brd(s2h_table)
s2h_cell = s2h_table.rows[0].cells[0]
bg(s2h_cell, C_BLUE)
cmar(s2h_cell, 80, 80, 120, 120)

s2h_p = s2h_cell.paragraphs[0]
fmt(s2h_p, align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=0)
run(s2h_p, '2 — OneDrive — Freigaben neu erstellen',
    bold=True, sz=10.5, col=C_WHITE)

# ── 10. SECTION 2 BODY ───────────────────────────────────────────────────────

s2b_table = add_table(doc, 1, 1)
box_brd(s2b_table, C_BRDBLU, sz=4)
s2b_cell = s2b_table.rows[0].cells[0]
bg(s2b_cell, C_SECTBG)
cmar(s2b_cell, 100, 100, 120, 120)

# Warning paragraph
warn_p = s2b_cell.paragraphs[0]
fmt(warn_p, align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=5, li=Cm(0.1))
set_para_shading(warn_p, C_WARNBG)
set_para_left_border(warn_p, C_RED, sz=16)
run(warn_p, '⚠  ', bold=True, sz=9, col=C_RED)
run(warn_p, 'Alle Freigaben mit dem alten UPN werden ', sz=8.5, col=C_WARNTX)
run(warn_p, 'automatisch ungültig.', bold=True, sz=8.5, col=C_WARNTX)
run(warn_p, ' Empfänger verlieren den Zugriff — jedes Element muss manuell neu geteilt werden.',
    sz=8.5, col=C_WARNTX)

# Steps for section 2
steps2 = [
    ('1', 'Alten Freigabe-Link deaktivieren',
     'In OneDrive (Web) zur geteilten Datei/Ordner navigieren → Rechtsklick → '
     'Zugriff verwalten → den alten Link entfernen oder deaktivieren.'),
    ('2', 'Neu teilen mit neuem UPN',
     'Erneut auf «Teilen» klicken und die neue geschäftliche E-Mail-Adresse '
     'als Absender-Konto verwenden. Empfänger per E-Mail neu einladen.'),
    ('3', 'Bestätigung einholen',
     'Sicherstellen, dass Empfänger den neuen Link erhalten haben und Zugriff '
     'funktioniert. Bei Problemen IT-Team kontaktieren.'),
]

for num, label, desc in steps2:
    lp = s2b_cell.add_paragraph()
    fmt(lp, align=WD_ALIGN_PARAGRAPH.LEFT, sb=4, sa=0)
    run(lp, num + '  ', bold=True, sz=12, col=C_BLUE)
    run(lp, label, bold=True, sz=9, col=C_DARK)

    dp = s2b_cell.add_paragraph()
    fmt(dp, align=WD_ALIGN_PARAGRAPH.LEFT, sb=0, sa=2, li=Cm(0.6))
    run(dp, desc, sz=8, col=C_DARK)

# ── 11. Gap ──────────────────────────────────────────────────────────────────
gap(doc, 4)

# ── 12. FOOTER ───────────────────────────────────────────────────────────────

footer_p = doc.add_paragraph()
fmt(footer_p, align=WD_ALIGN_PARAGRAPH.CENTER, sb=4, sa=0)

# Add top border to paragraph
pPr = footer_p._p.get_or_add_pPr()
pBdr = OxmlElement('w:pBdr')
top_brd = OxmlElement('w:top')
top_brd.set(qn('w:val'), 'single')
top_brd.set(qn('w:sz'), '4')
top_brd.set(qn('w:space'), '4')
top_brd.set(qn('w:color'), C_BRDGRY)
pBdr.append(top_brd)
pPr.append(pBdr)

run(footer_p, 'Bei Fragen wende dich an das IT-Team  ·  Internes Dokument',
    sz=7.5, col=C_HINT)

# ── Save ─────────────────────────────────────────────────────────────────────
doc.save(OUT_PATH)
print(f"SUCCESS: Document saved to {OUT_PATH}")
