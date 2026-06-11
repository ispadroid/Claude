#!/usr/bin/env python3
"""
Generate AXA corporate-design PPTX: UPN-Wechsel Kurzanleitung
A4 portrait (21 x 29.7 cm), single slide
"""

from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from lxml import etree
import copy

# ── Colours ─────────────────────────────────────────────────────────────────
AXA_BLUE   = RGBColor(0x00, 0x00, 0x8F)
AXA_RED    = RGBColor(0xFF, 0x17, 0x21)
TEXT_DARK  = RGBColor(0x34, 0x3C, 0x3D)
LIGHT_BLUE = RGBColor(0xEE, 0xEE, 0xF8)
LIGHT_RED  = RGBColor(0xFF, 0xF0, 0xF0)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GREY       = RGBColor(0x8C, 0x9B, 0xA5)
BORDER_BLUE= RGBColor(0xBB, 0xBB, 0xE8)
BORDER_GREY= RGBColor(0xCC, 0xCC, 0xCC)
DARK_RED   = RGBColor(0x8F, 0x00, 0x00)
MED_RED    = RGBColor(0xCC, 0x00, 0x00)
INTRO_BG   = RGBColor(0xF5, 0xF5, 0xF5)

# ── Slide dimensions ─────────────────────────────────────────────────────────
PAGE_W = Cm(21)
PAGE_H = Cm(29.7)
ML     = Cm(1.1)          # left margin
MR     = Cm(1.1)          # right margin
CW     = Cm(18.8)         # content width

# ── Helper: solid fill on shape ──────────────────────────────────────────────
def solid_fill(shape, rgb: RGBColor):
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = rgb

# ── Helper: add border to shape ──────────────────────────────────────────────
def add_border(shape, rgb: RGBColor, width_pt=0.5):
    ln = shape.line
    ln.color.rgb = rgb
    ln.width = Pt(width_pt)

# ── Helper: no line on shape ─────────────────────────────────────────────────
def no_line(shape):
    shape.line.fill.background()

# ── Helper: add plain textbox ────────────────────────────────────────────────
def add_textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    return tb, tf

# ── Helper: clear auto-margins on text frame ─────────────────────────────────
def zero_margins(tf):
    txBody = tf._txBody
    bodyPr = txBody.find(qn('a:bodyPr'))
    if bodyPr is not None:
        bodyPr.set('lIns', '45720')   # ~0.05 cm
        bodyPr.set('rIns', '45720')
        bodyPr.set('tIns', '36576')   # ~0.04 cm
        bodyPr.set('bIns', '36576')

def tight_margins(tf):
    txBody = tf._txBody
    bodyPr = txBody.find(qn('a:bodyPr'))
    if bodyPr is not None:
        bodyPr.set('lIns', '91440')
        bodyPr.set('rIns', '91440')
        bodyPr.set('tIns', '45720')
        bodyPr.set('bIns', '45720')

# ── Helper: run with font settings ──────────────────────────────────────────
def styled_run(para, text, size_pt, bold=False, italic=False,
               color=TEXT_DARK, font='Arial'):
    run = para.add_run()
    run.text = text
    rf = run.font
    rf.name = font
    rf.size = Pt(size_pt)
    rf.bold = bold
    rf.italic = italic
    rf.color.rgb = color
    return run

# ── Helper: add a rectangle shape ───────────────────────────────────────────
def add_rect(slide, x, y, w, h, fill_rgb=None, border_rgb=None,
             border_pt=0.5):
    from pptx.util import Emu
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        x, y, w, h
    )
    if fill_rgb:
        solid_fill(shape, fill_rgb)
    else:
        shape.fill.background()
    if border_rgb:
        add_border(shape, border_rgb, border_pt)
    else:
        no_line(shape)
    return shape

# ── Draw a step row ──────────────────────────────────────────────────────────
def draw_step(slide, x, y, w, h, num_text, num_color, label, body_text,
              body_color=TEXT_DARK, label_color=TEXT_DARK):
    """Draw one step: number | label (bold) + body text below, all inline."""
    NUM_W  = Cm(0.75)
    GAP    = Cm(0.15)
    TEXT_W = w - NUM_W - GAP

    # Number
    nb, ntf = add_textbox(slide, x, y, NUM_W, h)
    zero_margins(ntf)
    ntf.word_wrap = False
    p = ntf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    styled_run(p, num_text, 12, bold=True, color=num_color)

    # Label + body
    tb, tf = add_textbox(slide, x + NUM_W + GAP, y, TEXT_W, h)
    zero_margins(tf)
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    styled_run(p1, label, 8.5, bold=True, color=label_color)

    p2 = tf.add_paragraph()
    styled_run(p2, body_text, 7.8, bold=False, color=body_color)
    p2.space_before = Pt(1)

    return tb


# ════════════════════════════════════════════════════════════════════════════
# BUILD SLIDE
# ════════════════════════════════════════════════════════════════════════════

prs = Presentation()
prs.slide_width  = PAGE_W
prs.slide_height = PAGE_H

blank_layout = prs.slide_layouts[6]   # completely blank
slide = prs.slides.add_slide(blank_layout)

# ── Remove any placeholder shapes ────────────────────────────────────────────
for ph in slide.placeholders:
    sp = ph._element
    sp.getparent().remove(sp)

# ═══════════════════════════════════════════════════════════════════════════
# Vertical geometry (all heights fixed, positions computed top-to-bottom)
# ═══════════════════════════════════════════════════════════════════════════
TOP_OFFSET   = Cm(0.55)
H_HEADER     = Cm(2.0)
H_RED_BAR    = Cm(0.09)
H_INTRO      = Cm(0.95)
H_SEC_HDR    = Cm(0.58)
H_FOOTER     = Cm(0.65)
V_GAP        = Cm(0.12)   # small gap between sections

# Total fixed height
fixed = (TOP_OFFSET + H_HEADER + H_RED_BAR + V_GAP +
         H_INTRO + V_GAP +
         H_SEC_HDR +          # sec1 header
         V_GAP +
         H_SEC_HDR +          # sec2 header
         V_GAP +
         H_FOOTER)

remaining = PAGE_H - fixed
H_SEC1_BODY  = int(remaining * 0.55)
H_SEC2_BODY  = remaining - H_SEC1_BODY - V_GAP

# Y positions
y_header    = TOP_OFFSET
y_red_bar   = y_header + H_HEADER
y_intro     = y_red_bar + H_RED_BAR + V_GAP
y_sec1_hdr  = y_intro + H_INTRO + V_GAP
y_sec1_body = y_sec1_hdr + H_SEC_HDR
y_sec2_hdr  = y_sec1_body + H_SEC1_BODY + V_GAP
y_sec2_body = y_sec2_hdr + H_SEC_HDR
y_footer    = y_sec2_body + H_SEC2_BODY + V_GAP

# ═══════════════════════════════════════════════════════════════════════════
# 1. HEADER BAND
# ═══════════════════════════════════════════════════════════════════════════
hdr = add_rect(slide, ML, y_header, CW, H_HEADER, fill_rgb=AXA_BLUE)

# Text box inside header
tb, tf = add_textbox(slide, ML + Cm(0.3), y_header, CW - Cm(0.3), H_HEADER)
zero_margins(tf)

p1 = tf.paragraphs[0]
p1.alignment = PP_ALIGN.LEFT
styled_run(p1, 'AXA', 22, bold=True, color=WHITE)
styled_run(p1, '  |  ', 14, bold=False, color=WHITE)
styled_run(p1, 'UPN-Wechsel — Kurzanleitung', 14, bold=True, color=WHITE)

p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.LEFT
p2.space_before = Pt(3)
styled_run(p2, 'Was nach der Änderung deiner geschäftlichen E-Mail-Adresse zu tun ist',
           8.5, bold=False, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════
# 2. RED ACCENT BAR
# ═══════════════════════════════════════════════════════════════════════════
add_rect(slide, ML, y_red_bar, CW, H_RED_BAR, fill_rgb=AXA_RED)

# ═══════════════════════════════════════════════════════════════════════════
# 3. INTRO BOX
# ═══════════════════════════════════════════════════════════════════════════
intro_box = add_rect(slide, ML, y_intro, CW, H_INTRO,
                     fill_rgb=INTRO_BG, border_rgb=BORDER_GREY, border_pt=0.5)

tb, tf = add_textbox(slide, ML + Cm(0.2), y_intro + Cm(0.05),
                     CW - Cm(0.4), H_INTRO - Cm(0.1))
tight_margins(tf)
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.JUSTIFY
styled_run(p,
    'Dein User Principal Name (UPN) — deine geschäftliche E-Mail-Adresse — wurde geändert. '
    'Einige Microsoft-365-Apps müssen manuell neu verknüpft werden. '
    'Folge den Schritten — es dauert nur wenige Minuten.',
    8.5, color=TEXT_DARK)

# ═══════════════════════════════════════════════════════════════════════════
# 4. SECTION 1 HEADER
# ═══════════════════════════════════════════════════════════════════════════
add_rect(slide, ML, y_sec1_hdr, CW, H_SEC_HDR, fill_rgb=AXA_BLUE)
tb, tf = add_textbox(slide, ML + Cm(0.3), y_sec1_hdr, CW - Cm(0.3), H_SEC_HDR)
zero_margins(tf)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
styled_run(p, '1 — Microsoft OneNote — Notizbücher neu verknüpfen',
           10.5, bold=True, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════
# 5. SECTION 1 BODY
# ═══════════════════════════════════════════════════════════════════════════
add_rect(slide, ML, y_sec1_body, CW, H_SEC1_BODY,
         fill_rgb=LIGHT_BLUE, border_rgb=BORDER_BLUE, border_pt=0.6)

# Column widths
COL_GAP  = Cm(0.25)
LEFT_W   = CW * 0.60
RIGHT_W  = CW - LEFT_W - COL_GAP
X_LEFT   = ML + Cm(0.15)
X_RIGHT  = ML + LEFT_W + COL_GAP + Cm(0.15)

INNER_PAD_TOP = Cm(0.18)

# Steps data
steps = [
    ('⚠',  AXA_RED,  'Vor dem Schließen: Sync-Fehler prüfen',
     'Sicherstellen, dass keine Sync-Fehler vorhanden sind. '
     'Falls ja: betroffene Notizbücher zuerst manuell aus dem lokalen Ordner sichern.',
     AXA_RED),
    ('1',  AXA_BLUE, 'Alle Notizbücher schließen',
     'Rechtsklick auf jedes Notizbuch im linken Bereich → Notizbuch schließen '
     '(Close This Notebook). Für alle wiederholen, dann App beenden.',
     TEXT_DARK),
    ('2',  AXA_BLUE, 'Bei OneDrive Web mit neuer Adresse anmelden',
     'Browser öffnen → onedrive.com → mit der neuen geschäftlichen '
     'E-Mail-Adresse (neuem UPN) anmelden.',
     TEXT_DARK),
    ('3',  AXA_BLUE, 'Notizbuch direkt aus OneDrive Web öffnen',
     'Zum Ordner des Notizbuchs navigieren und darauf klicken: öffnet sich in '
     'OneNote für das Web. (Erzwingt die Neuverknüpfung mit dem neuen UPN.)',
     TEXT_DARK),
    ('4',  AXA_BLUE, 'In der Desktop-App weiterarbeiten',
     'In OneNote für das Web oben rechts auf «In OneNote öffnen» klicken. '
     'Das Notizbuch ist nun korrekt mit dem neuen Konto verknüpft.',
     TEXT_DARK),
]

N_STEPS   = len(steps)
body_inner_h = H_SEC1_BODY - INNER_PAD_TOP - Cm(0.1)
step_h    = body_inner_h // N_STEPS
step_gap  = Cm(0.06)

for i, (num, num_col, label, body, body_col) in enumerate(steps):
    sy = y_sec1_body + INNER_PAD_TOP + i * step_h
    draw_step(slide,
              X_LEFT, sy,
              LEFT_W - Cm(0.3), step_h - step_gap,
              num, num_col, label, body,
              body_color=body_col,
              label_color=num_col if num == '⚠' else TEXT_DARK)

# ── Screenshot (right column) ────────────────────────────────────────────────
IMG_PATH = '/root/.claude/uploads/cb3da536-4c85-53a7-8105-b6b8a4960349/bf765434-IMG_4052.png'

img_max_w = RIGHT_W - Cm(0.4)
img_max_h = H_SEC1_BODY - Cm(0.7)   # leave room for caption

# Original dimensions 345×351 → near-square
orig_w, orig_h = 345, 351
ratio = orig_w / orig_h
if img_max_w / ratio <= img_max_h:
    img_w = img_max_w
    img_h = img_max_w / ratio
else:
    img_h = img_max_h
    img_w = img_max_h * ratio

img_x = X_RIGHT + (RIGHT_W - img_w) / 2
img_y = y_sec1_body + Cm(0.15)

# White frame behind image
frame = add_rect(slide,
                 int(img_x - Cm(0.1)),
                 int(img_y - Cm(0.1)),
                 int(img_w + Cm(0.2)),
                 int(img_h + Cm(0.2)),
                 fill_rgb=WHITE,
                 border_rgb=BORDER_BLUE,
                 border_pt=0.5)

pic = slide.shapes.add_picture(IMG_PATH,
                                int(img_x), int(img_y),
                                int(img_w), int(img_h))

# Caption
cap_y = int(img_y + img_h + Cm(0.08))
cap_h = Cm(0.4)
tb, tf = add_textbox(slide, int(X_RIGHT), cap_y, int(RIGHT_W), cap_h)
zero_margins(tf)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
styled_run(p, 'Rechtsklick → Notizbuch schließen',
           7.5, italic=True, color=GREY)

# ═══════════════════════════════════════════════════════════════════════════
# 6. SECTION 2 HEADER
# ═══════════════════════════════════════════════════════════════════════════
add_rect(slide, ML, y_sec2_hdr, CW, H_SEC_HDR, fill_rgb=AXA_BLUE)
tb, tf = add_textbox(slide, ML + Cm(0.3), y_sec2_hdr, CW - Cm(0.3), H_SEC_HDR)
zero_margins(tf)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
styled_run(p, '2 — OneDrive — Freigaben neu erstellen',
           10.5, bold=True, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════
# 7. SECTION 2 BODY
# ═══════════════════════════════════════════════════════════════════════════
add_rect(slide, ML, y_sec2_body, CW, H_SEC2_BODY,
         fill_rgb=LIGHT_BLUE, border_rgb=BORDER_BLUE, border_pt=0.6)

WARN_H    = Cm(0.95)
WARN_PAD  = Cm(0.12)
warn_y    = y_sec2_body + WARN_PAD

# Warning background
warn_bg = add_rect(slide, ML + Cm(0.15), warn_y,
                   CW - Cm(0.3), WARN_H,
                   fill_rgb=LIGHT_RED)
# Left red border accent (thick vertical line)
warn_line = add_rect(slide, ML + Cm(0.15), warn_y,
                     Cm(0.18), WARN_H,
                     fill_rgb=AXA_RED)

# Warning text
tb, tf = add_textbox(slide,
                     ML + Cm(0.45), warn_y + Cm(0.06),
                     CW - Cm(0.65), WARN_H - Cm(0.12))
tight_margins(tf)
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT

styled_run(p, '⚠  ', 8.5, bold=True, color=AXA_RED)
styled_run(p, 'Alle Freigaben mit dem alten UPN werden ', 8.5, bold=False, color=DARK_RED)
styled_run(p, 'automatisch ungültig.', 8.5, bold=True, color=DARK_RED)
styled_run(p, ' Empfänger verlieren den Zugriff — jedes Element muss manuell neu geteilt werden.',
           8.5, bold=False, color=DARK_RED)

# Steps
steps2 = [
    ('1', 'Freigegebene Elemente finden',
     'Bei onedrive.com mit neuer Adresse anmelden → im linken Bereich auf '
     '«Geteilt» klicken → alle früheren Freigaben werden angezeigt.'),
    ('2', 'Jede Datei / jeden Ordner neu freigeben',
     'Rechtsklick → Freigeben → Empfänger eingeben → Berechtigung wählen '
     '(Anzeigen / Bearbeiten) → Senden.'),
    ('3', 'Empfänger über neuen Link informieren',
     'Alte Links funktionieren nicht mehr. Neue Einladung versenden oder Link '
     'direkt mitteilen. Für SharePoint-Bibliotheken das IT-Team kontaktieren.'),
]

steps_area_y  = warn_y + WARN_H + Cm(0.12)
steps_area_h  = H_SEC2_BODY - WARN_H - WARN_PAD * 2 - Cm(0.12)
step2_h       = steps_area_h // len(steps2)

for i, (num, label, body) in enumerate(steps2):
    sy = steps_area_y + i * step2_h
    draw_step(slide,
              ML + Cm(0.15), sy,
              CW - Cm(0.3), step2_h - Cm(0.05),
              num, AXA_BLUE, label, body,
              body_color=TEXT_DARK,
              label_color=TEXT_DARK)

# ═══════════════════════════════════════════════════════════════════════════
# 8. FOOTER
# ═══════════════════════════════════════════════════════════════════════════
# Divider line
div = add_rect(slide, ML, y_footer, CW, Cm(0.03), fill_rgb=BORDER_GREY)

# Footer text
tb, tf = add_textbox(slide, ML, y_footer + Cm(0.05), CW, H_FOOTER - Cm(0.05))
zero_margins(tf)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
styled_run(p, 'Bei Fragen wende dich an das IT-Team  ·  Internes Dokument',
           7.5, color=GREY)


# ═══════════════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════════════
OUT = '/home/user/Claude/UPN_Wechsel_AXA.pptx'
prs.save(OUT)

w_cm = prs.slide_width.cm
h_cm = prs.slide_height.cm
print(f'✓ Saved: {OUT}')
print(f'  Slide dimensions: {w_cm:.1f} cm × {h_cm:.1f} cm  (A4 portrait)')
print(f'  Sections: Header | Red bar | Intro | Sec1 ({H_SEC1_BODY/914400*2.54:.1f} cm) '
      f'| Sec2 ({H_SEC2_BODY/914400*2.54:.1f} cm) | Footer')
