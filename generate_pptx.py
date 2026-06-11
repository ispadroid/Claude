from pptx import Presentation
from pptx.util import Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

OUTPUT     = "/home/user/Claude/UPN_Wechsel_Handout.pptx"
SCREENSHOT = "/root/.claude/uploads/cb3da536-4c85-53a7-8105-b6b8a4960349/bf765434-IMG_4052.png"

# ── Colours ───────────────────────────────────────────────────────────────────
CD  = RGBColor(0x0F, 0x3D, 0x6E)   # blue dark
CM  = RGBColor(0x1B, 0x6E, 0xC2)   # blue mid
CL  = RGBColor(0xEA, 0xF2, 0xFD)   # blue light
CO  = RGBColor(0xC4, 0x5C, 0x00)   # orange
COB = RGBColor(0xFF, 0xF4, 0xEC)   # orange bg
CG  = RGBColor(0x2D, 0x2D, 0x2D)   # grey text
CGl = RGBColor(0xF4, 0xF6, 0xF9)   # grey light
CW  = RGBColor(0xFF, 0xFF, 0xFF)   # white
CB  = RGBColor(0xC0, 0xD4, 0xEE)   # border
CH  = RGBColor(0x55, 0x55, 0x55)   # hint
COT = RGBColor(0x5C, 0x28, 0x00)   # orange text dark

prs = Presentation()
prs.slide_width  = Cm(21)
prs.slide_height = Cm(29.7)
slide = prs.slides.add_slide(prs.slide_layouts[6])   # blank

# ── Primitive helpers ─────────────────────────────────────────────────────────
def box(x, y, w, h, fill, line=None, lw=0.5):
    s = slide.shapes.add_shape(1, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line: s.line.color.rgb = line; s.line.width = Pt(lw)
    else:    s.line.fill.background()
    return s

def tb(x, y, w, h, wrap=True):
    t = slide.shapes.add_textbox(x, y, w, h)
    t.text_frame.word_wrap = wrap
    return t.text_frame

def run(para, text, bold=False, italic=False, sz=9, col=None):
    r = para.add_run()
    r.text = text
    r.font.bold   = bold
    r.font.italic = italic
    r.font.size   = Pt(sz)
    if col: r.font.color.rgb = col
    return r

def para(tf, align=PP_ALIGN.LEFT, sb=0, sa=1):
    p = tf.add_paragraph()
    p.alignment = align; p.space_before = Pt(sb); p.space_after = Pt(sa)
    return p

# ── Layout ────────────────────────────────────────────────────────────────────
ML  = Cm(1.1)
PW  = prs.slide_width - ML * 2    # ~18.8 cm  (usable width)
PAD = Cm(0.35)                    # inner horizontal padding

# Fixed-height elements
HDR_H   = Cm(1.9)
ACC_H   = Cm(0.07)
INTRO_H = Cm(0.8)
SH_H    = Cm(0.58)                # section header height

# Vertical positions
MT      = Cm(0.55)
ACC_Y   = MT + HDR_H
INTRO_Y = ACC_Y + ACC_H + Cm(0.18)
S1_Y    = INTRO_Y + INTRO_H + Cm(0.28)   # section 1 header
B1_Y    = S1_Y + SH_H                    # body 1 start

# Section 2 & footer positioning
# Page bottom margin ~0.5 cm → last element ends at 29.7 - 0.5 = 29.2 cm
FOOT_H  = Cm(0.45)
DIV_H   = Cm(0.04)
PAGE_END = Cm(29.2)

# Split remaining space: body1 55%, body2 45%
GAPS    = Cm(0.28 + 0.28)          # gap before S2 header + gap before footer
FIXED   = B1_Y + SH_H + FOOT_H + DIV_H + GAPS
AVAIL   = PAGE_END - FIXED
B1_H    = AVAIL * 0.55
B2_H    = AVAIL * 0.45

S2_Y    = B1_Y + B1_H + Cm(0.28)
B2_Y    = S2_Y + SH_H
FOOT_Y  = B2_Y + B2_H + Cm(0.18)

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
box(ML, MT, PW, HDR_H, CD)
# title
f1 = tb(ML + PAD, MT + Cm(0.18), PW - Cm(3.5), HDR_H)
p0 = f1.paragraphs[0]; p0.alignment = PP_ALIGN.LEFT
run(p0, "UPN-Wechsel — Kurzanleitung", True, False, 17, CW)
p1 = para(f1, PP_ALIGN.LEFT, 0, 0)
run(p1, "Was nach der Änderung deiner geschäftlichen E-Mail-Adresse zu tun ist",
    False, False, 8.5, RGBColor(0xBD, 0xD6, 0xF5))
# M365 badge
f2 = tb(ML + PW - Cm(3.2), MT + Cm(0.6), Cm(3.0), Cm(0.8))
p2 = f2.paragraphs[0]; p2.alignment = PP_ALIGN.RIGHT
run(p2, "Microsoft 365", True, False, 10.5, RGBColor(0xBD, 0xD6, 0xF5))

# accent
box(ML, ACC_Y, PW, ACC_H, CO)

# ── Intro ─────────────────────────────────────────────────────────────────────
box(ML, INTRO_Y, PW, INTRO_H, CGl, CB, 0.5)
f3 = tb(ML + PAD, INTRO_Y + Cm(0.12), PW - PAD * 2, INTRO_H)
p3 = f3.paragraphs[0]; p3.alignment = PP_ALIGN.JUSTIFY
run(p3, "Dein ", False, False, 8.5, CG)
run(p3, "User Principal Name (UPN)", True, False, 8.5, CG)
run(p3, " — deine geschäftliche E-Mail-Adresse — wurde geändert. "
    "Einige Microsoft-365-Apps müssen manuell neu verknüpft werden. "
    "Folge den Schritten — es dauert nur wenige Minuten.", False, False, 8.5, CG)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ONENOTE
# ═══════════════════════════════════════════════════════════════════════════════
box(ML, S1_Y, PW, SH_H, CM)
fh1 = tb(ML + PAD, S1_Y + Cm(0.1), PW - PAD, SH_H)
run(fh1.paragraphs[0], "1 — Microsoft OneNote — Notizbücher neu verknüpfen",
    True, False, 10.5, CW)

box(ML, B1_Y, PW, B1_H, CL, CB, 0.5)

# ── Screenshot right column ───────────────────────────────────────────────────
IMG_W  = Cm(6.8)
IMG_H  = IMG_W * (351 / 345)
IMG_X  = ML + PW - IMG_W - Cm(0.45)
IMG_Y  = B1_Y + Cm(0.45)
box(IMG_X - Cm(0.18), IMG_Y - Cm(0.18),
    IMG_W + Cm(0.36), IMG_H + Cm(0.6), CW, CB, 0.9)
slide.shapes.add_picture(SCREENSHOT, IMG_X, IMG_Y, IMG_W, IMG_H)
fc = tb(IMG_X - Cm(0.2), IMG_Y + IMG_H + Cm(0.08), IMG_W + Cm(0.4), Cm(0.35))
pc = fc.paragraphs[0]; pc.alignment = PP_ALIGN.CENTER
run(pc, "Rechtsklick → Notizbuch schließen", False, True, 7.5, CH)

# ── Steps left column ─────────────────────────────────────────────────────────
LCW   = PW - IMG_W - Cm(1.6)      # left column width
LX    = ML + PAD                   # left column X
N_W   = Cm(0.7)                    # number cell width

steps1 = [
    ("⚠", "Vor dem Schließen: Sync-Fehler prüfen",
     "Sicherstellen, dass keine Sync-Fehler vorhanden sind. "
     "Falls ja: betroffene Notizbücher zuerst manuell aus dem lokalen Ordner sichern.",
     CO, CO),
    ("1", "Alle Notizbücher schließen",
     "Rechtsklick auf jedes Notizbuch im linken Bereich → "
     "Notizbuch schließen (Close This Notebook). Für alle wiederholen, dann App beenden.",
     CM, CG),
    ("2", "Bei OneDrive Web mit neuer Adresse anmelden",
     "Browser öffnen → onedrive.com aufrufen → mit der neuen "
     "geschäftlichen E-Mail-Adresse (neuem UPN) anmelden.",
     CM, CG),
    ("3", "Notizbuch direkt aus OneDrive Web öffnen",
     "Zum Ordner des Notizbuchs navigieren und darauf klicken: "
     "öffnet sich in OneNote für das Web. "
     "(Erzwingt die Neuverknüpfung mit dem neuen UPN.)",
     CM, CG),
    ("4", "In der Desktop-App weiterarbeiten",
     "In OneNote für das Web oben rechts auf «In OneNote öffnen» klicken. "
     "Das Notizbuch ist nun korrekt mit dem neuen Konto verknüpft.",
     CM, CG),
]

step_h = (B1_H - Cm(0.4)) / len(steps1)
for i, (num, lbl, txt, nc, tc) in enumerate(steps1):
    sy = B1_Y + Cm(0.2) + i * step_h
    fn = tb(LX, sy + Cm(0.04), N_W, step_h - Cm(0.1), False)
    run(fn.paragraphs[0], num, True, False, 13, nc)
    fr = tb(LX + N_W + Cm(0.1), sy, LCW - N_W - Cm(0.1), step_h)
    pr1 = fr.paragraphs[0]
    run(pr1, lbl, True, False, 9, CG)
    pr2 = para(fr, PP_ALIGN.LEFT, 0, 0)
    run(pr2, txt, False, False, 8, tc)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ONEDRIVE
# ═══════════════════════════════════════════════════════════════════════════════
box(ML, S2_Y, PW, SH_H, CM)
fh2 = tb(ML + PAD, S2_Y + Cm(0.1), PW - PAD, SH_H)
run(fh2.paragraphs[0], "2 — OneDrive — Freigaben neu erstellen", True, False, 10.5, CW)

box(ML, B2_Y, PW, B2_H, CL, CB, 0.5)

# Warning strip
WH = Cm(0.85)
box(ML + PAD, B2_Y + Cm(0.28), PW - PAD * 2, WH, COB, CO, 0.9)
fw = tb(ML + PAD + Cm(0.2), B2_Y + Cm(0.36), PW - PAD * 2 - Cm(0.4), WH)
pw1 = fw.paragraphs[0]
run(pw1, "⚠  ", True, False, 9, CO)
run(pw1, "Alle Freigaben mit dem alten UPN werden ", False, False, 8.5, COT)
run(pw1, "automatisch ungültig.", True, False, 8.5, COT)
run(pw1, " Empfänger verlieren den Zugriff — "
    "jedes Element muss manuell neu geteilt werden.", False, False, 8.5, COT)

steps2 = [
    ("1", "Freigegebene Elemente finden",
     "Bei onedrive.com mit neuer Adresse anmelden → "
     "im linken Bereich auf «Geteilt» klicken → alle früheren Freigaben werden angezeigt."),
    ("2", "Jede Datei / jeden Ordner neu freigeben",
     "Rechtsklick → Freigeben → Empfänger eingeben → "
     "Berechtigung wählen (Anzeigen / Bearbeiten) → Senden."),
    ("3", "Empfänger über neuen Link informieren",
     "Alte Links funktionieren nicht mehr. Neue Einladung versenden oder Link direkt mitteilen. "
     "Für SharePoint-Bibliotheken das IT-Team kontaktieren."),
]

step2_top  = B2_Y + WH + Cm(0.42)
step2_avail = B2_H - WH - Cm(0.7)
step2_h    = step2_avail / len(steps2)

for i, (num, lbl, txt) in enumerate(steps2):
    sy = step2_top + i * step2_h
    fn2 = tb(LX, sy + Cm(0.04), N_W, step2_h - Cm(0.1), False)
    run(fn2.paragraphs[0], num, True, False, 13, CM)
    fr2 = tb(LX + N_W + Cm(0.1), sy, PW - N_W - Cm(0.5), step2_h)
    pr1 = fr2.paragraphs[0]
    run(pr1, lbl, True, False, 9, CG)
    pr2 = para(fr2, PP_ALIGN.LEFT, 0, 0)
    run(pr2, txt, False, False, 8, CG)

# ── Footer ────────────────────────────────────────────────────────────────────
box(ML, FOOT_Y, PW, DIV_H, CB)
ff = tb(ML, FOOT_Y + Cm(0.1), PW, FOOT_H, False)
pf = ff.paragraphs[0]; pf.alignment = PP_ALIGN.CENTER
run(pf, "Bei Fragen wende dich an das IT-Team  ·  Internes Dokument",
    False, False, 7.5, CH)

prs.save(OUTPUT)
print(f"PPTX erstellt: {OUTPUT}")
