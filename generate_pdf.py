from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT     = "/home/user/Claude/UPN_Change_User_Guide.pdf"
SCREENSHOT = "/root/.claude/uploads/cb3da536-4c85-53a7-8105-b6b8a4960349/bf765434-IMG_4052.png"

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE_DARK  = colors.HexColor("#0F3D6E")
BLUE_MID   = colors.HexColor("#1B6EC2")
BLUE_LIGHT = colors.HexColor("#EAF2FD")
ORANGE     = colors.HexColor("#C45C00")
GREY_TEXT  = colors.HexColor("#3A3A3A")
GREY_LIGHT = colors.HexColor("#F4F6F9")
WHITE      = colors.white
BORDER     = colors.HexColor("#C5D8F5")

# ── Style helper ──────────────────────────────────────────────────────────────
def ps(name, **kw):
    base = getSampleStyleSheet()
    return ParagraphStyle(name + str(id(kw)), parent=base.get(name, base["Normal"]), **kw)

W, H = A4
ML = MR = 1.8 * cm
CONTENT_W = W - ML - MR

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=ML, rightMargin=MR,
    topMargin=0.8 * cm, bottomMargin=1.5 * cm
)

# ── Styles ────────────────────────────────────────────────────────────────────
s_title    = ps("Normal", fontName="Helvetica-Bold",    fontSize=20,  textColor=WHITE,    leading=26)
s_subtitle = ps("Normal", fontName="Helvetica",         fontSize=10,  textColor=colors.HexColor("#C8DEFF"), leading=14)
s_sec_hdr  = ps("Normal", fontName="Helvetica-Bold",    fontSize=12,  textColor=WHITE,    leading=16)
s_body     = ps("Normal", fontName="Helvetica",         fontSize=9.5, textColor=GREY_TEXT, leading=14, alignment=TA_JUSTIFY)
s_step_n   = ps("Normal", fontName="Helvetica-Bold",    fontSize=13,  textColor=BLUE_MID, leading=16)
s_step_lbl = ps("Normal", fontName="Helvetica-Bold",    fontSize=9.5, textColor=GREY_TEXT, leading=14, spaceAfter=2)
s_step_txt = ps("Normal", fontName="Helvetica",         fontSize=9,   textColor=GREY_TEXT, leading=13)
s_note     = ps("Normal", fontName="Helvetica-Oblique", fontSize=8.5, textColor=ORANGE,    leading=12)
s_caption  = ps("Normal", fontName="Helvetica-Oblique", fontSize=8,   textColor=colors.HexColor("#666666"), leading=11, alignment=TA_CENTER)
s_th       = ps("Normal", fontName="Helvetica-Bold",    fontSize=9,   textColor=WHITE,    leading=12, alignment=TA_CENTER)
s_td       = ps("Normal", fontName="Helvetica",         fontSize=9,   textColor=GREY_TEXT, leading=12)
s_td_b     = ps("Normal", fontName="Helvetica-Bold",    fontSize=9,   textColor=BLUE_DARK, leading=12)
s_footer   = ps("Normal", fontName="Helvetica",         fontSize=7.5, textColor=colors.HexColor("#888888"), leading=10, alignment=TA_CENTER)

story = []

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
hdr = Table(
    [[Paragraph("Cambio UPN — Guida Rapida per l'Utente", s_title),
      Paragraph("Microsoft<br/>365", ps("Normal", fontName="Helvetica-Bold", fontSize=13,
                 textColor=colors.HexColor("#C8DEFF"), leading=16, alignment=TA_CENTER))],
     [Paragraph("Cosa fare dopo il cambio del tuo indirizzo email aziendale", s_subtitle),
      Paragraph("", s_subtitle)]],
    colWidths=[CONTENT_W - 3 * cm, 3 * cm]
)
hdr.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,-1), BLUE_DARK),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("SPAN",         (1,0), (1,1)),
    ("LEFTPADDING",  (0,0), (0,-1), 14),
    ("LEFTPADDING",  (1,0), (1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING",   (0,0), (-1,0),  12),
    ("BOTTOMPADDING",(0,1), (-1,1),  12),
    ("TOPPADDING",   (0,1), (-1,1),  0),
    ("BOTTOMPADDING",(0,0), (-1,0),  2),
]))
story.append(hdr)

acc = Table([[""]], colWidths=[CONTENT_W], rowHeights=[4])
acc.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ORANGE),
                          ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                          ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
story.append(acc)
story.append(Spacer(1, 8))

intro = Table([[Paragraph(
    "Il tuo <b>User Principal Name (UPN)</b> — ovvero il tuo indirizzo email aziendale — è stato aggiornato. "
    "Alcune applicazioni Microsoft 365 richiedono pochi passaggi manuali per riallinearsi al nuovo account. "
    "Segui la guida qui sotto: bastano pochi minuti.", s_body)]],
    colWidths=[CONTENT_W])
intro.setStyle(TableStyle([
    ("BACKGROUND",   (0,0),(-1,-1), GREY_LIGHT),
    ("LEFTPADDING",  (0,0),(-1,-1), 12), ("RIGHTPADDING",(0,0),(-1,-1),12),
    ("TOPPADDING",   (0,0),(-1,-1),  8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ("BOX",          (0,0),(-1,-1), 0.5, BORDER),
]))
story.append(intro)
story.append(Spacer(1, 12))


# ── Builders ──────────────────────────────────────────────────────────────────
def sec_hdr(label, title):
    t = Table([[Paragraph(f"{label}  {title}", s_sec_hdr)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), BLUE_MID),
        ("LEFTPADDING",  (0,0),(-1,-1), 12), ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",   (0,0),(-1,-1),  7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    return t


def steps_with_screenshot(steps, screenshot_path, caption, preface=None):
    """Left column: numbered steps. Right column: screenshot."""
    step_rows = []
    if preface:
        step_rows.append([Paragraph("", s_body), preface])

    for num, lbl, txt, note in steps:
        items = [Paragraph(lbl, s_step_lbl), Paragraph(txt, s_step_txt)]
        if note:
            items.append(Paragraph(f"▸ {note}", s_note))
        right_tbl = Table([[it] for it in items],
                          colWidths=[None])
        right_tbl.setStyle(TableStyle([
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ]))
        step_rows.append([Paragraph(num, s_step_n), right_tbl])

    LEFT_W  = 0.5 * CONTENT_W
    IMG_W   = 0.5 * CONTENT_W - 1.2 * cm
    IMG_H   = IMG_W * (351 / 345)

    steps_tbl = Table(step_rows,
                      colWidths=[1.2*cm, LEFT_W - 1.2*cm])
    steps_tbl.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))

    img_cell = Table(
        [[Image(screenshot_path, width=IMG_W, height=IMG_H)],
         [Paragraph(caption, s_caption)]],
        colWidths=[IMG_W]
    )
    img_cell.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    img_box = Table([[img_cell]], colWidths=[IMG_W + 10])
    img_box.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),WHITE),
        ("BOX",(0,0),(-1,-1),0.8, BORDER),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))

    two_col = Table([[steps_tbl, img_box]],
                    colWidths=[LEFT_W, CONTENT_W - LEFT_W - 24])
    two_col.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))

    outer = Table([[two_col]], colWidths=[CONTENT_W])
    outer.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), BLUE_LIGHT),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("BOX",(0,0),(-1,-1),0.5, BORDER),
    ]))
    return outer


def step_table(steps, preface=None):
    rows = []
    if preface:
        rows.append([Paragraph("", s_body), preface])
    for num, lbl, txt, note in steps:
        items = [Paragraph(lbl, s_step_lbl), Paragraph(txt, s_step_txt)]
        if note:
            items.append(Paragraph(f"▸ {note}", s_note))
        right_tbl = Table([[it] for it in items],
                          colWidths=[CONTENT_W - 24 - 1.4*cm])
        right_tbl.setStyle(TableStyle([
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ]))
        rows.append([Paragraph(num, s_step_n), right_tbl])
    inner = Table(rows, colWidths=[1.2*cm, CONTENT_W - 24 - 1.2*cm])
    inner.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    outer = Table([[inner]], colWidths=[CONTENT_W])
    outer.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), BLUE_LIGHT),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),0.5, BORDER),
    ]))
    return outer


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ONENOTE
# ═══════════════════════════════════════════════════════════════════════════════
onenote_steps = [
    ("1", "Chiudi tutti i blocchi note aperti",
     "Nell'app OneNote fai <b>clic destro</b> su ogni blocco note nel pannello sinistro "
     "e seleziona <b>Chiudi blocco note</b> (Close This Notebook). "
     "Ripeti per tutti i blocchi note, poi chiudi l'app.",
     None),
    ("2", "Accedi a OneDrive Web con il nuovo indirizzo",
     "Apri il browser e vai su <b>onedrive.com</b>. "
     "Effettua il login con il <b>nuovo indirizzo email aziendale</b>.",
     None),
    ("3", "Apri il blocco note da OneDrive Web",
     "Naviga fino alla cartella del blocco note e fai clic su di esso: "
     "si aprirà in <b>OneNote per il Web</b>.",
     "Aprire da OneDrive Web forza il riallineamento al nuovo UPN."),
    ("4", "Rilancia nell'app desktop",
     "In OneNote per il Web clicca <b>\"Apri in OneNote\"</b> (in alto a destra). "
     "Il blocco note si apre nell'app correttamente collegato al nuovo account.",
     None),
]

story.append(KeepTogether([
    sec_hdr("1 —", "Microsoft OneNote — Ricollegare i blocchi note"),
    steps_with_screenshot(
        onenote_steps,
        SCREENSHOT,
        "Clic destro sul blocco note → Chiudi blocco note"
    ),
]))
story.append(Spacer(1, 10))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ONEDRIVE
# ═══════════════════════════════════════════════════════════════════════════════
pref = Paragraph(
    "Le condivisioni create con il vecchio UPN vengono <b>invalidate automaticamente</b>. "
    "I destinatari perderanno l'accesso. Ricondividi manualmente ogni elemento condiviso.",
    s_body)

onedrive_steps = [
    ("1", "Individua gli elementi precedentemente condivisi",
     "Accedi a <b>onedrive.com</b> con il nuovo indirizzo. "
     "Nel pannello sinistro clicca su <b>\"Condivisi\"</b> per visualizzare file e cartelle condivisi.",
     None),
    ("2", "Ricondividi ogni file o cartella",
     "Per ogni elemento: <b>clic destro → Condividi</b> → reinserisci i destinatari "
     "→ imposta il permesso (<b>Visualizzazione</b> o <b>Modifica</b>) → clicca <b>Invia</b>.",
     None),
    ("3", "Comunica il nuovo link ai destinatari",
     "I vecchi link <b>non funzioneranno più</b>. "
     "I destinatari riceveranno un nuovo invito oppure invia direttamente il nuovo link.",
     "Per file in raccolte SharePoint contatta il team IT per il riallineamento delle autorizzazioni."),
]

story.append(KeepTogether([
    sec_hdr("2 —", "OneDrive — Ricondivisione di file e cartelle"),
    step_table(onedrive_steps, preface=pref),
]))
story.append(Spacer(1, 10))

# ═══════════════════════════════════════════════════════════════════════════════
# RIEPILOGO
# ═══════════════════════════════════════════════════════════════════════════════
summary_data = [
    [Paragraph("Applicazione", s_th),
     Paragraph("Azione richiesta", s_th),
     Paragraph("Dove", s_th)],
    [Paragraph("Microsoft OneNote", s_td_b),
     Paragraph("Chiudi blocchi note → riapri da OneDrive Web → poi in app desktop", s_td),
     Paragraph("onedrive.com", s_td)],
    [Paragraph("OneDrive (condivisioni)", s_td_b),
     Paragraph("Ricondividi manualmente tutti i file e le cartelle condivisi", s_td),
     Paragraph("onedrive.com", s_td)],
    [Paragraph("SharePoint (raccolte)", s_td_b),
     Paragraph("Contatta il team IT per il riallineamento delle autorizzazioni", s_td),
     Paragraph("Team IT", s_td)],
]
summary_tbl = Table(summary_data, colWidths=[4.6*cm, CONTENT_W - 4.6*cm - 2.8*cm, 2.8*cm])
summary_tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), BLUE_DARK),
    ("BACKGROUND",(0,1),(-1,1), WHITE),
    ("BACKGROUND",(0,2),(-1,2), GREY_LIGHT),
    ("BACKGROUND",(0,3),(-1,3), WHITE),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
    ("GRID",(0,0),(-1,-1),0.4, BORDER),
    ("BOX",(0,0),(-1,-1),0.5, BORDER),
]))

story.append(KeepTogether([
    sec_hdr("", "Riepilogo"),
    summary_tbl,
]))
story.append(Spacer(1, 10))

# ── FOOTER ────────────────────────────────────────────────────────────────────
story.append(HRFlowable(width=CONTENT_W, thickness=0.5, color=colors.HexColor("#CCCCCC")))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Per assistenza contatta il team IT  ·  Documento riservato a uso interno",
    s_footer))

doc.build(story)
print(f"PDF generato: {OUTPUT}")
