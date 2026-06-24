# Mary Jo Nails — Contabilità 💅

**Zero-cost Swiss nail-artist accounting web app built on Google Apps Script.**

A simple Milchbüechli / Einnahmen-Ausgaben-Rechnung for a Swiss `Einzelfirma`.
No paid services. No local server. Runs entirely on free Google infrastructure.

---

## What's included

| Feature | Details |
|---|---|
| 💰 Nuovo incasso | Record a completed nail job in < 30 seconds |
| 🧾 Ricevuta PDF | Auto-generated, stored in Google Drive |
| ✉️ Email delivery | Optional, via Google MailApp (free quota) |
| 💬 WhatsApp sharing | Pre-filled message + wa.me link (manual) |
| 💸 Spese | Expense recording with categories + attachment upload |
| 📊 Dashboard | Monthly/yearly revenue, expenses, profit |
| ⏳ Pagamenti aperti | Track unpaid receipts |
| 📄 Jahresabschluss | Yearly closing PDF report |
| 💾 Backup & Export | JSON backup + CSV export saved to Drive |
| 🔐 PIN protection | SHA-256 hashed PIN, session tokens |
| 📱 Mobile-first | Optimized for iPhone Safari |

---

## File structure

All 17 files live at the root of the Apps Script project (no subdirectories):

```
appsscript.json      — manifest (Drive API v2, oauthScopes)
Code.gs              — doGet(), API bridge
Config.gs            — constants & defaults
Utils.gs             — shared utilities (hash, format, ID)
Database.gs          — Sheets setup & CRUD
DriveService.gs      — Drive folder management
Auth.gs              — PIN authentication & sessions
Sales.gs             — sales logic, receipt numbering
Expenses.gs          — expense recording
Reports.gs           — dashboard & yearly summaries
PdfService.gs        — PDF generation (HTML → Doc → PDF)
EmailService.gs      — MailApp sending
BackupService.gs     — CSV/JSON export
Styles.html          — mobile-first CSS (included in Index)
JavaScript.html      — client-side app JS (included in Index)
Index.html           — single-page app shell
README.md            — this file
```

---

## Deployment — Step by step

### 1. Create the Google Apps Script project

1. Go to [script.google.com](https://script.google.com) → **New project**.
2. Rename it (top-left) to `Mary Jo Nails - Contabilità`.

### 2. Copy all files

For each `.gs` file:
- In the Apps Script editor, click **+** next to **Files** → **Script**.
- Rename the file (without `.gs`).
- Paste the file content.

For each `.html` file:
- Click **+** → **HTML**.
- Rename to match (e.g., `Index`, `Styles`, `JavaScript`).
- Paste the content.

Replace the default `Code.gs` content with `Code.gs` from this repo.

For `appsscript.json`:
- In the editor click **Project Settings** (gear icon) → check **Show "appsscript.json" manifest file**.
- Click `appsscript.json` in the file list and replace its content.

### 3. Enable Drive API advanced service

In the Apps Script editor:
1. Click **+** next to **Services** (left panel).
2. Find **Drive API** → select **v2** → click **Add**.
3. Make sure the identifier is `Drive`.

### 4. Authorize permissions

Click **Run** → select any function (e.g., `getAppInitStatus`) → click **Authorize** →
follow the Google OAuth flow. Accept all permissions (Spreadsheets, Drive, Gmail).

### 5. Deploy as Web App

1. Click **Deploy** → **New deployment**.
2. Click the gear icon next to **Type** → select **Web app**.
3. Set:
   - **Execute as**: `Me` (your Google account)
   - **Who has access**: `Only myself` *(safest option)*
4. Click **Deploy**.
5. Copy the **Web App URL** — this is the app URL.

> **To update after code changes**: Deploy → Manage deployments → edit the existing deployment → **New version** → Save.

### 6. Access from iPhone

1. Open Safari on iPhone.
2. Navigate to the Web App URL.
3. Log in with PIN **1234** (default — change it immediately in Settings).

### 7. Add to iPhone Home Screen

1. In Safari, tap the **Share** button (box with arrow, bottom toolbar).
2. Tap **Add to Home Screen**.
3. Name it `Mary Jo Nails`.
4. Tap **Add**.

The app icon will appear on your Home Screen. It opens in fullscreen Safari.

> This is not a native app and not a full PWA. It runs in Safari. Internet connection is required.

### 8. First-run configuration

1. Open the app → enter PIN `1234`.
2. Go to **⚙️ Impostazioni**.
3. Enter your business name, owner name, address, phone, email.
4. Change the PIN immediately: tap **🔐 Cambia PIN**.
5. Go to **✂️ Servizi** to review and add your services with prices.

---

## Daily workflow

```
Open app → tap "💰 Nuovo incasso"
  → Select services / enter prices
  → Choose payment method
  → Tap "Salva e genera ricevuta"
  → PDF created in Google Drive automatically
  → Share by email or WhatsApp
```

**Target: 30 seconds per transaction.**

---

## Email sending

- Uses Google `MailApp` — **free quota: ~100 emails/day** for regular accounts.
- Enable in Settings → *Invio email abilitato: Sì*.
- Requires the customer's email address.
- PDF is attached automatically if already generated.
- Check quota: visible in Apps Script → Executions.

## WhatsApp sharing

- **No paid API used.**
- The app generates a pre-filled message in Italian.
- Tap **"Copia messaggio WhatsApp"** → paste in WhatsApp manually.
- If the customer has a phone number saved, a `wa.me` link opens WhatsApp with the message pre-filled.
- The PDF receipt must be attached manually from your phone's Files/Photos.

---

## Google Drive structure

Automatically created on first run:

```
📁 Mary Jo Nails - Contabilità/
  📁 Ricevute/
    📁 2026/    ← PDF receipts
  📁 Spese/
    📁 2026/    ← expense attachments
  📁 Jahresabschluss/
    📁 2026/    ← yearly closing PDFs
  📁 Backup/
    📁 2026/    ← JSON backups
  📁 Export/
    📁 2026/    ← CSV exports
```

The Google Spreadsheet database is also created automatically in your Drive root.

---

## Google Sheets database

Automatically created with these tabs:

| Tab | Contents |
|---|---|
| Settings | App configuration key-value pairs |
| Customers | Customer name, phone, email |
| Services | Service catalogue with prices |
| Sales | All receipts / income records |
| SaleItems | Line items for each sale |
| Expenses | All business expenses |
| PrivateTransactions | Privatbezüge / Privateinlagen |
| DeliveryLogs | Email/WhatsApp delivery attempts |
| YearClosings | Yearly closing summaries |
| AuditLog | Audit trail of all changes |

**All money values are stored as integer cents (Rappen) to avoid floating-point errors.**

---

## Yearly closing (Jahresabschluss)

1. Go to **📊 Jahresabschluss**.
2. Select the year.
3. Review the summary (revenue, expenses, profit, open receivables, private transactions).
4. Add notes if needed.
5. Tap **Genera report PDF** — a formatted PDF is saved to Drive and opened in browser.

The report clearly states:
> *"Questo è un semplice rendiconto Milchbüechli / Einnahmen-Ausgaben-Rechnung per una piccola Einzelfirma svizzera."*

---

## Security

### Access protection
- App-level PIN (SHA-256 hashed, stored in Script Properties — never plain text).
- Session tokens in Google's server-side CacheService (expire after 8 hours).
- All sensitive server functions validate the session token before executing.

### Deployment recommendation
- Deploy with **Execute as: Me** + **Access: Only myself**.
- This means only your Google account can open the web app.
- The PIN adds a second layer inside the app.

### Important limitations
- If someone gains access to your Google account, they can access the app data.
- If the web app is accidentally deployed as public, only the PIN protects data.
- Do not share the Web App URL publicly.
- Enable 2-factor authentication (2FA) on your Google account.

---

## MWST / IVA thresholds (Switzerland)

The app warns you when:

| Threshold | What it means |
|---|---|
| CHF 100'000/year | **Voluntary/mandatory MWST registration** may apply |
| CHF 500'000/year | **Ordinary accounting** (Milchbüechli no longer sufficient) |

These are informational warnings only. Consult a `Treuhänder` (fiduciary) for tax advice.

---

## Known limitations

| Limitation | Notes |
|---|---|
| Not double-entry bookkeeping | This is a simple Einnahmen-Ausgaben-Rechnung, not a full accounting system |
| No automatic tax filing | Export data for your fiduciary/tax declaration |
| WhatsApp attachment is manual | The zero-cost version cannot auto-attach PDFs to WhatsApp |
| Email quota | ~100 emails/day for free Google accounts |
| Apps Script execution timeout | 6 minutes max per execution (sufficient for all operations here) |
| Apps Script daily quotas | See [Google quotas](https://developers.google.com/apps-script/guides/services/quotas) |
| No offline mode | Internet required |
| PDF quality | HTML→Doc→PDF conversion may not preserve complex CSS |
| Single user | Designed for one owner, not multi-user |
| No native app | Opens in Safari, not from App Store |

---

## Google Apps Script quotas (free tier)

| Resource | Free quota |
|---|---|
| Script runtime | 6 min/execution, 90 min/day |
| Email (MailApp) | 100 messages/day |
| Drive storage | 15 GB (shared with Gmail) |
| URL Fetch | 20,000 calls/day |
| Spreadsheet reads/writes | 5,000,000 cells/day |

For a small nail studio, these limits are far above normal usage.

---

## Exporting data for a fiduciary

1. Go to **💾 Backup & Export**.
2. Select the year.
3. Tap **Esporta tutti i CSV** — creates:
   - `Vendite_[year].csv` — all sales
   - `DettaglioVendite_[year].csv` — sale line items
   - `Spese_[year].csv` — all expenses
   - `Transazioni_Private_[year].csv` — private transactions
4. Also tap **Crea backup ora** for a complete JSON backup.
5. All files appear as links to Google Drive.

Share the CSV files and the Jahresabschluss PDF with your fiduciary.

---

## What this app does NOT do

- Does not automatically file taxes (Steuererklärung).
- Does not replace professional fiduciary/tax advice.
- Does not handle payroll (Lohnbuchhaltung) — for sole proprietors only.
- Does not manage inventory.
- Does not send appointment reminders.
- Does not handle MWST calculation (not registered by default).
- Does not connect to Abacus, Bexio, or any other accounting software.

---

## Next improvements (future roadmap)

- [ ] Appointment calendar integration (Google Calendar)
- [ ] Recurring customers / loyalty tracking
- [ ] Photo gallery for nail art work
- [ ] Multi-language reports (DE/IT/FR)
- [ ] MWST calculation when registered
- [ ] Automatic monthly email summary
- [ ] Barcode/QR scanner for expense receipts
- [ ] Budget targets per expense category

---

## License

This project was created for personal use as a zero-cost Swiss small business tool.
It is not an audited financial system and does not replace professional accounting software or fiduciary advice.

---

*Generato con Google Apps Script. Nessun costo aggiuntivo. 💅*
