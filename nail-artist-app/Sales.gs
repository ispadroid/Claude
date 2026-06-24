// Sales.gs — Sale creation, receipt numbers, and sales queries.

// ---------------------------------------------------------------------------
// Receipt number generation — uses LockService to prevent duplicates
// ---------------------------------------------------------------------------
function generateReceiptNumber(year) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var key = 'LAST_RECEIPT_SEQ_' + year;
    var props = PropertiesService.getScriptProperties();
    var last = parseInt(props.getProperty(key) || '0');

    // Also verify against actual sheet data (safety net)
    var sheetMax = getMaxReceiptSeqFromSheet(year);
    var seq = Math.max(last, sheetMax) + 1;

    props.setProperty(key, seq.toString());
    return buildReceiptNumber(year, seq);
  } finally {
    lock.releaseLock();
  }
}

function getMaxReceiptSeqFromSheet(year) {
  var rows = getSheetRows(CONFIG.SHEETS.SALES);
  var prefix = year.toString() + '-';
  var max = 0;
  rows.forEach(function(r) {
    if (r.receiptNumber && r.receiptNumber.toString().startsWith(prefix)) {
      var n = parseInt(r.receiptNumber.toString().replace(prefix, '')) || 0;
      if (n > max) max = n;
    }
  });
  return max;
}

// ---------------------------------------------------------------------------
// Create sale
// ---------------------------------------------------------------------------
function createSale(data) {
  // data: { date, customerName, customerPhone, customerEmail, items[], paymentMethod,
  //         paymentStatus, discountCents, tipCents, notes }
  var now = getCurrentTimestamp();
  var year = getCurrentYear();

  // Validate required fields
  if (!data.items || data.items.length === 0) {
    return { success: false, error: 'Aggiungi almeno un servizio.' };
  }
  if (CONFIG.PAYMENT_METHODS.indexOf(data.paymentMethod) === -1) {
    return { success: false, error: 'Metodo di pagamento non valido.' };
  }

  // Upsert customer
  var customerId = '';
  if (data.customerName) {
    customerId = upsertCustomer(data.customerName, data.customerPhone, data.customerEmail) || '';
  }

  // Calculate totals (all in cents)
  var subtotalCents = data.items.reduce(function(sum, item) {
    return sum + safeInt(item.totalCents);
  }, 0);
  var discountCents = safeInt(data.discountCents);
  var tipCents = safeInt(data.tipCents);
  var totalCents = subtotalCents - discountCents + tipCents;

  var saleId = generateId();
  var receiptNumber = generateReceiptNumber(year);
  var saleDate = data.date || formatDateISO(new Date());
  var paymentStatus = data.paymentStatus || 'Pagato';

  var saleRow = {
    saleId: saleId,
    receiptNumber: receiptNumber,
    date: saleDate,
    customerId: customerId,
    customerNameSnapshot: sanitizeString(data.customerName),
    paymentMethod: sanitizeString(data.paymentMethod),
    paymentStatus: paymentStatus,
    subtotalCents: subtotalCents,
    discountCents: discountCents,
    tipCents: tipCents,
    totalCents: totalCents,
    notes: sanitizeString(data.notes),
    receiptPdfFileId: '',
    receiptPdfUrl: '',
    status: 'active',
    createdAt: now,
    updatedAt: now
  };

  appendRowBySchema(CONFIG.SHEETS.SALES, saleRow);

  // Save sale items
  data.items.forEach(function(item) {
    appendRowBySchema(CONFIG.SHEETS.SALE_ITEMS, {
      saleItemId: generateId(),
      saleId: saleId,
      description: sanitizeString(item.description),
      quantity: safeInt(item.quantity) || 1,
      unitPriceCents: safeInt(item.unitPriceCents),
      totalCents: safeInt(item.totalCents)
    });
  });

  writeAuditLog('Sale', saleId, 'created', { receiptNumber: receiptNumber, totalCents: totalCents });

  // Generate PDF immediately
  var pdfResult = { fileId: '', url: '', error: null };
  try {
    pdfResult = generateReceiptPdf(saleId);
  } catch (e) {
    pdfResult.error = e.message;
    Logger.log('PDF generation error: ' + e.message);
  }

  return {
    success: true,
    saleId: saleId,
    receiptNumber: receiptNumber,
    totalCents: totalCents,
    pdfFileId: pdfResult.fileId,
    pdfUrl: pdfResult.url,
    pdfError: pdfResult.error,
    customerName: sanitizeString(data.customerName),
    customerPhone: sanitizeString(data.customerPhone),
    customerEmail: sanitizeString(data.customerEmail)
  };
}

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------
function getSales(year, month) {
  var rows = getSheetRows(CONFIG.SHEETS.SALES)
    .filter(function(r) { return r.status !== 'cancelled'; })
    .sort(function(a, b) {
      return new Date(b.createdAt) - new Date(a.createdAt);
    });

  if (year) {
    rows = rows.filter(function(r) {
      return r.date && r.date.toString().startsWith(year.toString());
    });
  }
  if (month) {
    var mm = month.toString().padStart(2, '0');
    rows = rows.filter(function(r) {
      return r.date && r.date.toString().startsWith(year.toString() + '-' + mm);
    });
  }
  return rows;
}

function getSaleById(saleId) {
  var sale = findRowById(CONFIG.SHEETS.SALES, 'saleId', saleId);
  if (!sale) return null;
  var items = getSheetRows(CONFIG.SHEETS.SALE_ITEMS)
    .filter(function(i) { return i.saleId === saleId; });
  return { sale: sale, items: items };
}

function getOpenPayments() {
  return getSheetRows(CONFIG.SHEETS.SALES).filter(function(r) {
    return r.status !== 'cancelled' &&
      (r.paymentStatus === 'Aperto' || r.paymentStatus === 'Pagato parzialmente');
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------
function markSaleAsPaid(saleId) {
  updateRowById(CONFIG.SHEETS.SALES, 'saleId', saleId, {
    paymentStatus: 'Pagato',
    updatedAt: getCurrentTimestamp()
  });
  writeAuditLog('Sale', saleId, 'marked_paid', {});
  return { success: true };
}

function cancelSale(saleId, reason) {
  updateRowById(CONFIG.SHEETS.SALES, 'saleId', saleId, {
    status: 'cancelled',
    notes: (findRowById(CONFIG.SHEETS.SALES, 'saleId', saleId) || {}).notes + ' [Storniert: ' + reason + ']',
    updatedAt: getCurrentTimestamp()
  });
  writeAuditLog('Sale', saleId, 'cancelled', { reason: reason });
  return { success: true };
}

function logDelivery(saleId, channel, recipient, status, errorMessage) {
  appendRowBySchema(CONFIG.SHEETS.DELIVERY_LOGS, {
    deliveryLogId: generateId(),
    saleId: saleId,
    channel: channel,
    recipient: recipient,
    status: status,
    errorMessage: errorMessage || '',
    sentAt: getCurrentTimestamp()
  });
}

// ---------------------------------------------------------------------------
// WhatsApp message helper
// ---------------------------------------------------------------------------
function buildWhatsAppMessage(saleId) {
  var result = getSaleById(saleId);
  if (!result) return { success: false, error: 'Vendita non trovata.' };
  var sale = result.sale;
  var settings = getSettings();
  var biz = settings.businessName || CONFIG.APP_NAME;
  var name = sale.customerNameSnapshot || 'cliente';
  var amount = formatMoneyPlain(sale.totalCents);
  var msg = 'Ciao ' + name + ', grazie per essere venuta da ' + biz + '! ' +
    'Ti invio la ricevuta ' + sale.receiptNumber + ' di CHF ' + amount + '. ' +
    'Grazie per la tua fiducia! 💅';
  var phone = '';
  if (sale.customerId) {
    var customer = findRowById(CONFIG.SHEETS.CUSTOMERS, 'customerId', sale.customerId);
    if (customer) phone = customer.phone || '';
  }
  var waLink = '';
  if (phone) {
    var clean = phone.replace(/[^0-9+]/g, '');
    waLink = 'https://wa.me/' + clean + '?text=' + encodeURIComponent(msg);
  }
  logDelivery(saleId, 'whatsapp', phone || 'unknown', 'prepared', '');
  return { success: true, message: msg, phone: phone, waLink: waLink, pdfUrl: sale.receiptPdfUrl };
}
