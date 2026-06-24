// PdfService.gs — PDF generation for receipts and yearly closing reports.
// Uses Drive API v2 to convert HTML → Google Doc → PDF blob.

function generateReceiptPdf(saleId) {
  var data = getSaleById(saleId);
  if (!data) throw new Error('Vendita non trovata: ' + saleId);
  var sale = data.sale;
  var items = data.items;
  var settings = getSettings();
  var year = sale.date ? sale.date.toString().substring(0, 4) : getCurrentYear().toString();

  var html = buildReceiptHtml(sale, items, settings);
  var fileName = 'Ricevuta_' + sale.receiptNumber;
  var pdfBlob = htmlToPdfBlob(html, fileName);

  var folder = getReceiptsFolder(parseInt(year));
  var file = folder.createFile(pdfBlob.setName(fileName + '.pdf'));

  // Update sale record with PDF info
  updateRowById(CONFIG.SHEETS.SALES, 'saleId', saleId, {
    receiptPdfFileId: file.getId(),
    receiptPdfUrl: file.getUrl(),
    updatedAt: getCurrentTimestamp()
  });

  return { fileId: file.getId(), url: file.getUrl() };
}

function generateYearlyClosingPdf(year, summary, notes) {
  var settings = getSettings();
  var html = buildYearlyClosingHtml(year, summary, settings, notes);
  var fileName = 'Jahresabschluss_' + year;
  var pdfBlob = htmlToPdfBlob(html, fileName);

  var folder = getYearClosingFolder(year);
  var file = folder.createFile(pdfBlob.setName(fileName + '.pdf'));
  return { fileId: file.getId(), url: file.getUrl() };
}

// ---------------------------------------------------------------------------
// HTML → PDF conversion via Drive API v2
// ---------------------------------------------------------------------------
function htmlToPdfBlob(htmlContent, fileName) {
  var blob = Utilities.newBlob(htmlContent, MimeType.HTML, fileName + '.html');
  var file = Drive.Files.insert(
    { title: fileName, mimeType: 'application/vnd.google-apps.document' },
    blob
  );
  var pdfBlob = DriveApp.getFileById(file.id).getAs(MimeType.PDF);
  DriveApp.getFileById(file.id).setTrashed(true);
  return pdfBlob;
}

// ---------------------------------------------------------------------------
// Receipt HTML template
// ---------------------------------------------------------------------------
function buildReceiptHtml(sale, items, settings) {
  var biz = settings.businessName || CONFIG.APP_NAME;
  var owner = settings.ownerName || '';
  var address = (settings.address || '').replace(/\n/g, '<br>');
  var phone = settings.phone || '';
  var email = settings.email || '';
  var website = settings.website || '';
  var vatMode = settings.vatMode || 'not_registered';

  var itemRows = items.map(function(i) {
    return '<tr>' +
      '<td style="padding:6px 4px;border-bottom:1px solid #eee;">' + escHtml(i.description) + '</td>' +
      '<td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:center;">' + safeInt(i.quantity) + '</td>' +
      '<td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:right;">CHF ' + formatMoneyPlain(i.unitPriceCents) + '</td>' +
      '<td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:right;">CHF ' + formatMoneyPlain(i.totalCents) + '</td>' +
      '</tr>';
  }).join('');

  var discountRow = '';
  if (safeInt(sale.discountCents) > 0) {
    discountRow = '<tr><td colspan="3" style="padding:4px;text-align:right;color:#e74c3c;">Sconto:</td>' +
      '<td style="padding:4px;text-align:right;color:#e74c3c;">- CHF ' + formatMoneyPlain(sale.discountCents) + '</td></tr>';
  }
  var tipRow = '';
  if (safeInt(sale.tipCents) > 0) {
    tipRow = '<tr><td colspan="3" style="padding:4px;text-align:right;">Mancia:</td>' +
      '<td style="padding:4px;text-align:right;">CHF ' + formatMoneyPlain(sale.tipCents) + '</td></tr>';
  }

  var vatNote = (vatMode === 'not_registered')
    ? '<p style="font-size:11px;color:#777;margin-top:16px;border-top:1px solid #eee;padding-top:8px;">Nicht MWST-pflichtig / IVA non applicata</p>'
    : '';

  var customerBlock = sale.customerNameSnapshot
    ? '<p><strong>Cliente:</strong> ' + escHtml(sale.customerNameSnapshot) + '</p>'
    : '';

  var websiteBlock = website
    ? '<p>' + escHtml(website) + '</p>'
    : '';

  return '<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8">' +
    '<style>body{font-family:Arial,sans-serif;font-size:13px;color:#333;margin:40px;} ' +
    'h1{font-size:22px;margin:0;} h2{font-size:16px;color:#555;} ' +
    'table{width:100%;border-collapse:collapse;} ' +
    'th{background:#f5f5f5;padding:8px 4px;text-align:left;font-size:12px;border-bottom:2px solid #ddd;} ' +
    '.total-row td{font-weight:bold;font-size:15px;border-top:2px solid #333;padding:8px 4px;}</style></head>' +
    '<body>' +
    '<table style="width:100%;margin-bottom:24px;"><tr>' +
    '<td><h1>' + escHtml(biz) + '</h1>' +
    (owner ? '<p>' + escHtml(owner) + '</p>' : '') +
    '<p style="color:#555;">' + address + '</p>' +
    (phone ? '<p>Tel: ' + escHtml(phone) + '</p>' : '') +
    (email ? '<p>' + escHtml(email) + '</p>' : '') +
    websiteBlock + '</td>' +
    '<td style="text-align:right;vertical-align:top;">' +
    '<h2 style="color:#c0392b;">RICEVUTA</h2>' +
    '<p><strong>N°</strong> ' + escHtml(sale.receiptNumber) + '</p>' +
    '<p><strong>Data:</strong> ' + formatDate(sale.date) + '</p>' +
    '</td></tr></table>' +
    customerBlock +
    '<table style="margin-top:16px;">' +
    '<tr><th>Descrizione</th><th style="text-align:center;">Qtà</th><th style="text-align:right;">Prezzo unit.</th><th style="text-align:right;">Totale</th></tr>' +
    itemRows +
    '<tr><td colspan="3" style="padding:4px;text-align:right;color:#555;">Subtotale:</td>' +
    '<td style="padding:4px;text-align:right;">CHF ' + formatMoneyPlain(sale.subtotalCents) + '</td></tr>' +
    discountRow + tipRow +
    '<tr class="total-row"><td colspan="3" style="text-align:right;">TOTALE:</td>' +
    '<td style="text-align:right;">CHF ' + formatMoneyPlain(sale.totalCents) + '</td></tr>' +
    '</table>' +
    '<p style="margin-top:16px;"><strong>Pagamento:</strong> ' + escHtml(sale.paymentMethod) +
    ' — <strong>Stato:</strong> ' + escHtml(sale.paymentStatus) + '</p>' +
    (sale.notes ? '<p><em>' + escHtml(sale.notes) + '</em></p>' : '') +
    vatNote +
    '<p style="text-align:center;margin-top:24px;font-size:13px;color:#555;">Grazie per la tua visita! 💅</p>' +
    '</body></html>';
}

// ---------------------------------------------------------------------------
// Yearly closing HTML template
// ---------------------------------------------------------------------------
function buildYearlyClosingHtml(year, summary, settings, notes) {
  var biz = settings.businessName || CONFIG.APP_NAME;
  var owner = settings.ownerName || '';

  function row(label, cents, color) {
    var style = color ? ' style="color:' + color + ';"' : '';
    return '<tr><td style="padding:6px 8px;border-bottom:1px solid #eee;">' + label + '</td>' +
      '<td style="padding:6px 8px;border-bottom:1px solid #eee;text-align:right;"' + style + '>' +
      formatMoney(cents) + '</td></tr>';
  }

  var catRows = Object.keys(summary.expenseByCategory || {}).map(function(cat) {
    return row('&nbsp;&nbsp;&nbsp;' + escHtml(cat), summary.expenseByCategory[cat]);
  }).join('');

  var payRows = Object.keys(summary.paymentSplit || {}).map(function(m) {
    return row(escHtml(m), summary.paymentSplit[m]);
  }).join('');

  return '<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8">' +
    '<style>body{font-family:Arial,sans-serif;font-size:13px;color:#333;margin:40px;} ' +
    'h1{font-size:20px;} h2{font-size:15px;color:#555;margin-top:24px;} ' +
    'table{width:100%;border-collapse:collapse;} ' +
    '.total{font-weight:bold;font-size:15px;background:#f5f5f5;} ' +
    '.disclaimer{font-size:11px;color:#999;border:1px solid #ddd;padding:12px;margin-top:24px;}</style></head>' +
    '<body>' +
    '<h1>' + escHtml(biz) + ' — Jahresabschluss ' + year + '</h1>' +
    (owner ? '<p>' + escHtml(owner) + '</p>' : '') +
    '<p>Chiusura annuale / Jahresabschluss per l\'anno fiscale ' + year + '</p>' +

    '<h2>Einnahmen / Entrate</h2>' +
    '<table>' +
    row('Totale ricavi (CHF)', summary.revenueCents, '#27ae60') +
    row('Numero ricevute emesse', summary.receiptCount) +
    '</table>' +

    '<h2>Ausgaben / Spese</h2>' +
    '<table>' +
    row('Totale spese deducibili (CHF)', summary.expenseCents, '#e74c3c') +
    catRows +
    '</table>' +

    '<h2>Ergebnis / Risultato</h2>' +
    '<table>' +
    '<tr class="total"><td style="padding:8px;">Gewinn / Utile netto</td>' +
    '<td style="padding:8px;text-align:right;' + (summary.profitCents >= 0 ? 'color:#27ae60;' : 'color:#e74c3c;') + '">' +
    formatMoney(summary.profitCents) + '</td></tr>' +
    '</table>' +

    '<h2>Private Transaktionen / Transazioni private</h2>' +
    '<table>' +
    row('Prelievi privati (Privatbezüge)', summary.privateWithdrawalsCents) +
    row('Apporti privati (Privateinlagen)', summary.privateContributionsCents) +
    '</table>' +

    '<h2>Offene Forderungen / Crediti aperti</h2>' +
    '<table>' +
    row('Importo non ancora incassato', summary.openReceivablesCents, '#e67e22') +
    '</table>' +

    '<h2>Zahlungsarten / Metodi di pagamento</h2>' +
    '<table>' + payRows + '</table>' +

    (notes ? '<h2>Note</h2><p>' + escHtml(notes) + '</p>' : '') +

    '<div class="disclaimer">' +
    '<strong>Nota:</strong> Questo è un semplice rendiconto Milchbüechli / Einnahmen-Ausgaben-Rechnung ' +
    'per una piccola Einzelfirma svizzera. Non si tratta di un bilancio certificato. ' +
    'Non sostituisce la consulenza di un fiduciario o fiscalista. ' +
    'Generato il ' + formatDate(new Date()) + '.</div>' +
    '</body></html>';
}

function escHtml(s) {
  if (!s) return '';
  return s.toString()
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
