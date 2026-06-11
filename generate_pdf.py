from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT

OUTPUT     = "/home/user/Claude/UPN_Wechsel_Handout.pdf"
SCREENSHOT = "/root/.claude/uploads/cb3da536-4c85-53a7-8105-b6b8a4960349/bf765434-IMG_4052.png"

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE_DARK  = colors.HexColor("#0F3D6E")
BLUE_MID   = colors.HexColor("#1B6EC2")
BLUE_LIGHT = colors.HexColor("#EAF2FD")
ORANGE     = colors.HexColor("#C45C00")
GREY_TEXT  = colors.HexColor("#2D2D2D")
GREY_LIGHT = colors.HexColor("#F4F6F9")
WHITE      = colors.white
BORDER     = colors.HexColor("#C0D4EE")
GREEN      = colors.HexColor("#107C10")

def ps(base="Normal", **kw):
    b = getSampleStyleSheet().get(base, getSampleStyleSheet()["Normal"])
    return ParagraphStyle(base + str(id(kw)), parent=b, **kw)

W, H   = A4
ML = MR = 1.2 * cm
MT = 0.7 * cm
MB = 1.0 * cm
CW = W - ML - MR                           # usable content width

doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                        leftMargin=ML, rightMargin=MR,
                        topMargin=MT, bottomMargin=MB)

# ── Styles ────────────────────────────────────────────────────────────────────
T  = lambda txt, st: Paragraph(txt, st)
SH = ps(fontName="Helvetica-Bold",    fontSize=18, textColor=WHITE,   leading=22)
SS = ps(fontName="Helvetica",         fontSize=9,  textColor=colors.HexColor("#BDD6F5"), leading=12)
SE = ps(fontName="Helvetica-Bold",    fontSize=9.5,textColor=WHITE,   leading=13)
SI = ps(fontName="Helvetica",         fontSize=8.5,textColor=GREY_TEXT,leading=12, alignment=TA_JUSTIFY)
SN = ps(fontName="Helvetica-Bold",    fontSize=11, textColor=BLUE_MID,leading=14)
SL = ps(fontName="Helvetica-Bold",    fontSize=8.5,textColor=GREY_TEXT,leading=12, spaceAfter=1)
ST = ps(fontName="Helvetica",         fontSize=8,  textColor=GREY_TEXT,leading=11)
SO = ps(fontName="Helvetica-Oblique", fontSize=7.5,textColor=ORANGE,  leading=10)
SC = ps(fontName="Helvetica-Oblique", fontSize=7,  textColor=colors.HexColor("#555"),leading=9, alignment=TA_CENTER)
TH = ps(fontName="Helvetica-Bold",    fontSize=8,  textColor=WHITE,   leading=11, alignment=TA_CENTER)
TD = ps(fontName="Helvetica",         fontSize=8,  textColor=GREY_TEXT,leading=11)
TB = ps(fontName="Helvetica-Bold",    fontSize=8,  textColor=BLUE_DARK,leading=11)
SF = ps(fontName="Helvetica",         fontSize=7,  textColor=colors.HexColor("#888"),leading=9, alignment=TA_CENTER)

# ── Helpers ───────────────────────────────────────────────────────────────────
def pad(t, l=6, r=6, top=4, bot=4, bg=None):
    s = [("LEFTPADDING",(0,0),(-1,-1),l), ("RIGHTPADDING",(0,0),(-1,-1),r),
         ("TOPPADDING", (0,0),(-1,-1),top),("BOTTOMPADDING",(0,0),(-1,-1),bot)]
    if bg: s.append(("BACKGROUND",(0,0),(-1,-1),bg))
    t.setStyle(TableStyle(s))
    return t

def sec_header(num, title):
    label = f"{num} — {title}" if num else title
    t = Table([[T(label, SE)]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE_MID),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    return t

def step_block(rows_data):
    """rows_data: list of (num, label, text, note|None)"""
    rows = []
    for num, lbl, txt, note in rows_data:
        items = [T(lbl, SL), T(txt, ST)]
        if note:
            items.append(T(f"▸ {note}", SO))
        rt = Table([[x] for x in items], colWidths=[None])
        rt.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                                 ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
        rows.append([T(num, SN), rt])
    t = Table(rows, colWidths=[0.9*cm, None])
    t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def outer_box(inner_table, width=CW):
    t = Table([[inner_table]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE_LIGHT),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("BOX",(0,0),(-1,-1),0.5,BORDER),
    ]))
    return t

# ═══════════════════════════════════════════════════════════════════════════════
story = []

# ── HEADER ────────────────────────────────────────────────────────────────────
hdr = Table([
    [T("UPN-Wechsel — Kurzanleitung", SH),
     T("Microsoft 365", ps(fontName="Helvetica-Bold", fontSize=11,
        textColor=colors.HexColor("#BDD6F5"), leading=14, alignment=TA_RIGHT))],
    [T("Was nach der Änderung deiner geschäftlichen E-Mail-Adresse zu tun ist", SS),
     T("", SS)],
], colWidths=[CW - 3*cm, 3*cm])
hdr.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),BLUE_DARK),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("SPAN",(1,0),(1,1)),
    ("LEFTPADDING",(0,0),(0,-1),12),("LEFTPADDING",(1,0),(1,-1),6),
    ("RIGHTPADDING",(0,0),(-1,-1),10),
    ("TOPPADDING",(0,0),(-1,0),10),("BOTTOMPADDING",(0,0),(-1,0),2),
    ("TOPPADDING",(0,1),(-1,1),0),("BOTTOMPADDING",(0,1),(-1,1),10),
]))
story.append(hdr)

# orange accent line
acc = Table([[""]], colWidths=[CW], rowHeights=[3])
acc.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ORANGE),
    ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
story.append(acc)
story.append(Spacer(1, 5))

# ── INTRO ─────────────────────────────────────────────────────────────────────
intro = Table([[T(
    "Dein <b>User Principal Name (UPN)</b> — deine geschäftliche E-Mail-Adresse — wurde geändert. "
    "Einige Microsoft-365-Apps müssen manuell neu verknüpft werden. Folge den Schritten unten — "
    "es dauert nur wenige Minuten.", SI)]], colWidths=[CW])
intro.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GREY_LIGHT),
    ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
    ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ("BOX",(0,0),(-1,-1),0.5,BORDER)]))
story.append(intro)
story.append(Spacer(1, 7))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ONENOTE  (steps left, screenshot right)
# ═══════════════════════════════════════════════════════════════════════════════
one_steps = [
    ("1", "Alle Notizbücher schließen",
     "In der OneNote-App <b>rechtsklick</b> auf jedes Notizbuch im linken Bereich "
     "→ <b>Notizbuch schließen</b> (Close This Notebook). Für alle wiederholen, dann App beenden.",
     None),
    ("2", "Bei OneDrive Web mit neuer Adresse anmelden",
     "Browser öffnen → <b>onedrive.com</b> aufrufen → mit der <b>neuen geschäftlichen "
     "E-Mail-Adresse</b> (neuem UPN) anmelden.",
     None),
    ("3", "Notizbuch direkt aus OneDrive Web öffnen",
     "Zum Ordner des Notizbuchs navigieren und darauf klicken: "
     "es öffnet sich in <b>OneNote für das Web</b>.",
     "Öffnen über OneDrive Web erzwingt die Neuverknüpfung mit dem neuen UPN."),
    ("4", "In der Desktop-App weiterarbeiten",
     "In OneNote für das Web oben rechts auf <b>«In OneNote öffnen»</b> klicken. "
     "Das Notizbuch wird korrekt mit dem neuen Konto verknüpft.",
     None),
]

LEFT_W = CW * 0.58
RIGHT_W = CW - LEFT_W

# screenshot sized to fit right column
IMG_RATIO = 351 / 345
IMG_W = RIGHT_W - 1.4 * cm
IMG_H = IMG_W * IMG_RATIO

steps_inner = step_block(one_steps)

img_inner = Table([
    [Image(SCREENSHOT, width=IMG_W, height=IMG_H)],
    [T("Rechtsklick → Notizbuch schließen", SC)],
], colWidths=[IMG_W])
img_inner.setStyle(TableStyle([
    ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),2),
    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
]))
img_box = Table([[img_inner]], colWidths=[IMG_W + 10])
img_box.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),WHITE),
    ("BOX",(0,0),(-1,-1),0.8,BORDER),
    ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
]))

two_col = Table([[steps_inner, img_box]],
                colWidths=[LEFT_W - 20, RIGHT_W - 4])
two_col.setStyle(TableStyle([
    ("VALIGN",(0,0),(-1,-1),"TOP"),
    ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(1,0),(1,-1),0),
    ("RIGHTPADDING",(0,0),(0,-1),8),
]))

story.append(sec_header("1", "Microsoft OneNote — Notizbücher neu verknüpfen"))
story.append(outer_box(two_col))
story.append(Spacer(1, 6))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ONEDRIVE
# ═══════════════════════════════════════════════════════════════════════════════
warn = Table([[T(
    "⚠  Alle Freigaben, die mit dem alten UPN erstellt wurden, werden <b>automatisch ungültig</b>. "
    "Empfänger verlieren den Zugriff. Jedes freigegebene Element muss manuell neu geteilt werden.",
    ps(fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#5C2800"),
       leading=11, alignment=TA_JUSTIFY))]],
    colWidths=[CW - 20])
warn.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#FFF4EC")),
    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("BOX",(0,0),(-1,-1),0.8,ORANGE),
]))

od_steps = [
    ("1", "Freigegebene Elemente finden",
     "Bei <b>onedrive.com</b> mit neuer Adresse anmelden → im linken Bereich "
     "auf <b>«Geteilt»</b> klicken → alle früher freigegebenen Dateien und Ordner werden angezeigt.",
     None),
    ("2", "Jede Datei / jeden Ordner neu freigeben",
     "<b>Rechtsklick → Freigeben</b> → Empfänger erneut eingeben → "
     "Berechtigung festlegen (<b>Anzeigen</b> oder <b>Bearbeiten</b>) → <b>Senden</b>.",
     None),
    ("3", "Empfänger über den neuen Link informieren",
     "Alte Freigabelinks funktionieren <b>nicht mehr</b>. "
     "Empfänger erhalten eine neue Einladung oder du sendest den neuen Link direkt.",
     "Für Dateien in SharePoint-Bibliotheken das IT-Team kontaktieren."),
]

od_inner = Table([[warn], [step_block(od_steps)]], colWidths=[CW - 20])
od_inner.setStyle(TableStyle([
    ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ("BOTTOMPADDING",(0,0),(0,0),5),
]))

story.append(sec_header("2", "OneDrive — Freigaben neu erstellen"))
story.append(outer_box(od_inner))
story.append(Spacer(1, 6))

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
C1, C3 = 4.2*cm, 2.4*cm
C2 = CW - C1 - C3

sum_data = [
    [T("Anwendung",        TH), T("Erforderliche Aktion", TH), T("Wo",   TH)],
    [T("Microsoft OneNote",TB), T("Notizbücher schließen → aus OneDrive Web öffnen → in Desktop-App", TD), T("onedrive.com", TD)],
    [T("OneDrive (Freigaben)",TB), T("Alle freigegebenen Dateien und Ordner manuell neu teilen", TD), T("onedrive.com", TD)],
    [T("SharePoint",       TB), T("IT-Team für Berechtigungsanpassung kontaktieren", TD), T("IT-Team", TD)],
]
sum_tbl = Table(sum_data, colWidths=[C1, C2, C3])
sum_tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),BLUE_DARK),
    ("BACKGROUND",(0,1),(-1,1),WHITE),
    ("BACKGROUND",(0,2),(-1,2),GREY_LIGHT),
    ("BACKGROUND",(0,3),(-1,3),WHITE),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("GRID",(0,0),(-1,-1),0.4,BORDER),
    ("BOX",(0,0),(-1,-1),0.5,BORDER),
]))

story.append(sec_header("", "Auf einen Blick"))
story.append(sum_tbl)
story.append(Spacer(1, 6))

# ── FOOTER ────────────────────────────────────────────────────────────────────
story.append(HRFlowable(width=CW, thickness=0.4, color=colors.HexColor("#CCCCCC")))
story.append(Spacer(1, 3))
story.append(T("Bei Fragen wende dich an das IT-Team  ·  Internes Dokument", SF))

# ── BUILD ─────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF erstellt: {OUTPUT}")
