// EmailService.gs — Receipt email delivery via GmailApp / MailApp.

function sendReceiptByEmail(saleId, recipientEmail) {
  var data = getSaleById(saleId);
  if (!data) return { success: false, error: 'Vendita non trovata.' };
  var sale = data.sale;

  var email = sanitizeString(recipientEmail || sale.customerNameSnapshot);
  // Try to get customer email if not provided
  if (!email || !email.includes('@')) {
    if (sale.customerId) {
      var customer = findRowById(CONFIG.SHEETS.CUSTOMERS, 'customerId', sale.customerId);
      if (customer) email = customer.email || '';
    }
  }
  if (!email || !email.includes('@')) {
    return { success: false, error: 'Email del cliente non disponibile. Inserisci un indirizzo email valido.' };
  }

  var settings = getSettings();
  var biz = settings.businessName || CONFIG.APP_NAME;
  var subject = 'Ricevuta ' + sale.receiptNumber + ' — ' + biz;

  var body = 'Gentile ' + (sale.customerNameSnapshot || 'cliente') + ',\n\n' +
    'Grazie per la tua visita da ' + biz + '!\n' +
    'In allegato trovi la ricevuta ' + sale.receiptNumber + ' del ' + formatDate(sale.date) +
    ' per un totale di ' + formatMoney(sale.totalCents) + '.\n\n' +
    'Pagamento: ' + sale.paymentMethod + ' — ' + sale.paymentStatus + '\n\n' +
    'A presto! 💅\n' + biz;

  // Attach PDF
  var attachment = null;
  if (sale.receiptPdfFileId) {
    try {
      var pdfFile = DriveApp.getFileById(sale.receiptPdfFileId);
      attachment = pdfFile.getBlob();
    } catch (e) {
      Logger.log('Could not load PDF: ' + e.message);
    }
  }

  // If no PDF exists yet, generate it
  if (!attachment) {
    try {
      var pdfResult = generateReceiptPdf(saleId);
      if (pdfResult.fileId) {
        attachment = DriveApp.getFileById(pdfResult.fileId).getBlob();
      }
    } catch (e) {
      Logger.log('PDF gen error for email: ' + e.message);
    }
  }

  try {
    var mailOptions = {
      name: biz,
      subject: subject,
      body: body
    };
    if (attachment) mailOptions.attachments = [attachment];

    MailApp.sendEmail(email, subject, body, mailOptions);
    logDelivery(saleId, 'email', email, 'sent', '');
    return { success: true, sentTo: email };
  } catch (e) {
    logDelivery(saleId, 'email', email, 'error', e.message);
    return { success: false, error: 'Errore invio email: ' + e.message };
  }
}

function getRemainingEmailQuota() {
  try {
    return MailApp.getRemainingDailyQuota();
  } catch (e) {
    return -1;
  }
}
