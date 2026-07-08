// Expenses.gs — Expense recording and queries.

function createExpense(data) {
  var now = getCurrentTimestamp();

  if (!data.date) return { success: false, error: 'Data obbligatoria.' };
  if (!data.amountCents || safeInt(data.amountCents) <= 0) {
    return { success: false, error: 'Importo non valido.' };
  }

  var amountCents = safeInt(data.amountCents);
  var businessPct = safeInt(data.businessPercentage);
  if (businessPct < 0 || businessPct > 100) businessPct = 100;
  var deductibleCents = Math.round(amountCents * businessPct / 100);

  var expenseId = generateId();
  appendRowBySchema(CONFIG.SHEETS.EXPENSES, {
    expenseId: expenseId,
    date: sanitizeString(data.date),
    vendor: sanitizeString(data.vendor),
    category: sanitizeString(data.category),
    amountCents: amountCents,
    businessPercentage: businessPct,
    deductibleAmountCents: deductibleCents,
    paymentMethod: sanitizeString(data.paymentMethod),
    notes: sanitizeString(data.notes),
    attachmentFileId: data.attachmentFileId || '',
    attachmentUrl: data.attachmentUrl || '',
    status: 'active',
    createdAt: now,
    updatedAt: now
  });

  writeAuditLog('Expense', expenseId, 'created', { amountCents: amountCents });
  return { success: true, expenseId: expenseId };
}

function createExpenseWithAttachment(data) {
  // Handle optional base64 attachment
  var attachFileId = '';
  var attachUrl = '';
  if (data.attachmentBase64 && data.attachmentMimeType && data.attachmentFileName) {
    var year = data.date ? data.date.substring(0, 4) : getCurrentYear().toString();
    var result = saveExpenseAttachment(data.attachmentBase64, data.attachmentMimeType, data.attachmentFileName, year);
    attachFileId = result.fileId;
    attachUrl = result.url;
  }
  data.attachmentFileId = attachFileId;
  data.attachmentUrl = attachUrl;
  delete data.attachmentBase64;
  delete data.attachmentMimeType;
  delete data.attachmentFileName;
  return createExpense(data);
}

function getExpenses(year, month) {
  var rows = getSheetRows(CONFIG.SHEETS.EXPENSES)
    .filter(function(r) { return r.status !== 'cancelled'; })
    .sort(function(a, b) { return new Date(b.date) - new Date(a.date); });

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

function getExpenseById(expenseId) {
  return findRowById(CONFIG.SHEETS.EXPENSES, 'expenseId', expenseId);
}

function deleteExpense(expenseId) {
  updateRowById(CONFIG.SHEETS.EXPENSES, 'expenseId', expenseId, {
    status: 'cancelled',
    updatedAt: getCurrentTimestamp()
  });
  writeAuditLog('Expense', expenseId, 'cancelled', {});
  return { success: true };
}

// ---------------------------------------------------------------------------
// Private transactions
// ---------------------------------------------------------------------------
function createPrivateTransaction(data) {
  var now = getCurrentTimestamp();
  var id = generateId();
  appendRowBySchema(CONFIG.SHEETS.PRIVATE_TRANSACTIONS, {
    privateTransactionId: id,
    date: sanitizeString(data.date),
    type: data.type === 'contribution' ? 'Privateinlage' : 'Privatbezug',
    amountCents: safeInt(data.amountCents),
    notes: sanitizeString(data.notes),
    createdAt: now,
    updatedAt: now
  });
  writeAuditLog('PrivateTransaction', id, 'created', { type: data.type, amountCents: data.amountCents });
  return { success: true, id: id };
}

function getPrivateTransactions(year) {
  var rows = getSheetRows(CONFIG.SHEETS.PRIVATE_TRANSACTIONS);
  if (year) {
    rows = rows.filter(function(r) {
      return r.date && r.date.toString().startsWith(year.toString());
    });
  }
  return rows;
}
