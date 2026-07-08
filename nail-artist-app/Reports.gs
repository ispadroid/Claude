// Reports.gs — Dashboard data, monthly and yearly summaries.

function getDashboardData() {
  var year = getCurrentYear();
  var month = getCurrentMonth();

  var allSales = getSheetRows(CONFIG.SHEETS.SALES).filter(function(r) { return r.status !== 'cancelled'; });
  var allExpenses = getSheetRows(CONFIG.SHEETS.EXPENSES).filter(function(r) { return r.status !== 'cancelled'; });

  var yearPrefix = year.toString();
  var monthPrefix = year.toString() + '-' + month.toString().padStart(2, '0');

  var yearSales = allSales.filter(function(r) { return r.date && r.date.toString().startsWith(yearPrefix); });
  var monthSales = allSales.filter(function(r) { return r.date && r.date.toString().startsWith(monthPrefix); });
  var yearExpenses = allExpenses.filter(function(r) { return r.date && r.date.toString().startsWith(yearPrefix); });
  var monthExpenses = allExpenses.filter(function(r) { return r.date && r.date.toString().startsWith(monthPrefix); });

  var yearRevenue = sumCents(yearSales, 'totalCents');
  var monthRevenue = sumCents(monthSales, 'totalCents');
  var yearExpense = sumCents(yearExpenses, 'deductibleAmountCents');
  var monthExpense = sumCents(monthExpenses, 'deductibleAmountCents');

  var openPayments = allSales.filter(function(r) {
    return r.paymentStatus === 'Aperto' || r.paymentStatus === 'Pagato parzialmente';
  });
  var openAmount = sumCents(openPayments, 'totalCents');

  // Payment method split for this year
  var paymentSplit = {};
  yearSales.forEach(function(r) {
    var m = r.paymentMethod || 'Altro';
    paymentSplit[m] = (paymentSplit[m] || 0) + safeInt(r.totalCents);
  });

  // Top services
  var serviceRevenue = {};
  var saleItems = getSheetRows(CONFIG.SHEETS.SALE_ITEMS);
  var activeSaleIds = new Set(yearSales.map(function(s) { return s.saleId; }));
  saleItems.filter(function(i) { return activeSaleIds.has(i.saleId); }).forEach(function(i) {
    var desc = i.description || 'Servizio';
    serviceRevenue[desc] = (serviceRevenue[desc] || 0) + safeInt(i.totalCents);
  });
  var topServices = Object.keys(serviceRevenue)
    .map(function(k) { return { name: k, totalCents: serviceRevenue[k] }; })
    .sort(function(a, b) { return b.totalCents - a.totalCents; })
    .slice(0, 5);

  // Monthly overview for the current year (last 12 months)
  var monthlyOverview = [];
  for (var m = 1; m <= 12; m++) {
    var mp = year.toString() + '-' + m.toString().padStart(2, '0');
    var ms = allSales.filter(function(r) { return r.date && r.date.toString().startsWith(mp); });
    var me = allExpenses.filter(function(r) { return r.date && r.date.toString().startsWith(mp); });
    var rev = sumCents(ms, 'totalCents');
    var exp = sumCents(me, 'deductibleAmountCents');
    monthlyOverview.push({
      month: m,
      label: monthName(m),
      revenueCents: rev,
      expenseCents: exp,
      profitCents: rev - exp
    });
  }

  // Warnings
  var warnings = [];
  if (yearRevenue >= CONFIG.MWST_THRESHOLD_CENTS) {
    warnings.push('⚠️ Fatturato annuo supera CHF 100\'000! Verifica l\'obbligo di registrazione MWST.');
  } else if (yearRevenue >= CONFIG.MWST_THRESHOLD_CENTS * 0.8) {
    warnings.push('📢 Fatturato annuo si avvicina a CHF 100\'000 (soglia MWST). Consulta un fiduciario.');
  }
  if (yearRevenue >= CONFIG.ORDINARY_ACCOUNTING_THRESHOLD_CENTS) {
    warnings.push('⚠️ Fatturato supera CHF 500\'000. Potrebbe essere necessaria la contabilità ordinaria.');
  }

  return {
    year: year,
    month: month,
    yearRevenueCents: yearRevenue,
    monthRevenueCents: monthRevenue,
    yearExpenseCents: yearExpense,
    monthExpenseCents: monthExpense,
    yearProfitCents: yearRevenue - yearExpense,
    monthProfitCents: monthRevenue - monthExpense,
    openAmountCents: openAmount,
    openCount: openPayments.length,
    yearReceiptCount: yearSales.length,
    paymentSplit: paymentSplit,
    topServices: topServices,
    monthlyOverview: monthlyOverview,
    warnings: warnings
  };
}

function getYearlySummary(year) {
  var yearStr = year.toString();
  var sales = getSheetRows(CONFIG.SHEETS.SALES).filter(function(r) {
    return r.status !== 'cancelled' && r.date && r.date.toString().startsWith(yearStr);
  });
  var expenses = getSheetRows(CONFIG.SHEETS.EXPENSES).filter(function(r) {
    return r.status !== 'cancelled' && r.date && r.date.toString().startsWith(yearStr);
  });
  var privateTx = getPrivateTransactions(year);

  var revenueCents = sumCents(sales, 'totalCents');
  var expenseCents = sumCents(expenses, 'deductibleAmountCents');
  var profitCents = revenueCents - expenseCents;
  var privateWithdrawalsCents = sumCents(
    privateTx.filter(function(t) { return t.type === 'Privatbezug'; }), 'amountCents');
  var privateContributionsCents = sumCents(
    privateTx.filter(function(t) { return t.type === 'Privateinlage'; }), 'amountCents');

  var openPayments = getOpenPayments();
  var openReceivablesCents = sumCents(openPayments, 'totalCents');

  // Expense by category
  var expenseByCategory = {};
  expenses.forEach(function(e) {
    var cat = e.category || 'Altro';
    expenseByCategory[cat] = (expenseByCategory[cat] || 0) + safeInt(e.deductibleAmountCents);
  });

  // Payment method split
  var paymentSplit = {};
  sales.forEach(function(s) {
    var m = s.paymentMethod || 'Altro';
    paymentSplit[m] = (paymentSplit[m] || 0) + safeInt(s.totalCents);
  });

  return {
    year: year,
    revenueCents: revenueCents,
    expenseCents: expenseCents,
    profitCents: profitCents,
    privateWithdrawalsCents: privateWithdrawalsCents,
    privateContributionsCents: privateContributionsCents,
    openReceivablesCents: openReceivablesCents,
    receiptCount: sales.length,
    expenseCount: expenses.length,
    expenseByCategory: expenseByCategory,
    paymentSplit: paymentSplit
  };
}

function saveYearClosing(data) {
  var now = getCurrentTimestamp();
  var existing = getSheetRows(CONFIG.SHEETS.YEAR_CLOSINGS)
    .find(function(r) { return r.year && r.year.toString() === data.year.toString(); });

  var summary = getYearlySummary(data.year);

  var closingId = existing ? existing.yearClosingId : generateId();
  var row = {
    yearClosingId: closingId,
    year: data.year,
    revenueCents: summary.revenueCents,
    expenseCents: summary.expenseCents,
    profitCents: summary.profitCents,
    privateWithdrawalsCents: summary.privateWithdrawalsCents,
    privateContributionsCents: summary.privateContributionsCents,
    openReceivablesCents: summary.openReceivablesCents,
    notes: sanitizeString(data.notes),
    pdfFileId: data.pdfFileId || (existing ? existing.pdfFileId : ''),
    pdfUrl: data.pdfUrl || (existing ? existing.pdfUrl : ''),
    createdAt: existing ? existing.createdAt : now,
    updatedAt: now
  };

  if (existing) {
    updateRowById(CONFIG.SHEETS.YEAR_CLOSINGS, 'yearClosingId', closingId, row);
  } else {
    appendRowBySchema(CONFIG.SHEETS.YEAR_CLOSINGS, row);
  }

  writeAuditLog('YearClosing', closingId, existing ? 'updated' : 'created', { year: data.year });
  return { success: true, closingId: closingId, summary: summary };
}

function generateYearlyClosingReport(year, notes) {
  var summary = getYearlySummary(year);
  var result = saveYearClosing({ year: year, notes: notes || '' });
  try {
    var pdfResult = generateYearlyClosingPdf(year, summary, notes);
    if (pdfResult.fileId) {
      updateRowById(CONFIG.SHEETS.YEAR_CLOSINGS, 'yearClosingId', result.closingId, {
        pdfFileId: pdfResult.fileId,
        pdfUrl: pdfResult.url,
        updatedAt: getCurrentTimestamp()
      });
    }
    return { success: true, summary: summary, pdfUrl: pdfResult.url, pdfFileId: pdfResult.fileId };
  } catch (e) {
    return { success: true, summary: summary, pdfUrl: '', pdfError: e.message };
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function sumCents(rows, field) {
  return rows.reduce(function(sum, r) { return sum + safeInt(r[field]); }, 0);
}

function monthName(m) {
  var names = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];
  return names[m - 1] || m.toString();
}
