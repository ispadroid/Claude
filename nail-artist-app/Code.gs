// Code.gs — Web app entry point and HTML template helper.
// Deploy as: Execute as "Me", Access "Only myself" (or domain if needed).

function doGet(e) {
  var template = HtmlService.createTemplateFromFile('Index');
  return template.evaluate()
    .setTitle('Mary Jo Nails 💅')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
    .addMetaTag('apple-mobile-web-app-capable', 'yes')
    .addMetaTag('apple-mobile-web-app-status-bar-style', 'default')
    .addMetaTag('theme-color', '#c0392b');
}

function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

// ---------------------------------------------------------------------------
// API bridge — all functions callable via google.script.run must be top-level.
// Auth wrapper validates session before executing sensitive operations.
// ---------------------------------------------------------------------------

// Auth
function api_getInitStatus() { return getAppInitStatus(); }
function api_verifyPin(pin) { return verifyPin(pin); }
function api_changePin(current, next) { return changePin(current, next); }
function api_logout(token) { return logout(token); }
function api_validateSession(token) { return { valid: validateSession(token) }; }

// Settings
function api_getSettings(token) {
  if (!validateSession(token)) return authError();
  return getSettings();
}
function api_saveSettings(token, data) {
  if (!validateSession(token)) return authError();
  return saveSettings(data);
}

// Services
function api_getServices(token) {
  if (!validateSession(token)) return authError();
  return getServices();
}
function api_getAllServices(token) {
  if (!validateSession(token)) return authError();
  return getAllServices();
}
function api_saveService(token, data) {
  if (!validateSession(token)) return authError();
  return saveService(data);
}

// Customers
function api_getCustomers(token) {
  if (!validateSession(token)) return authError();
  return getCustomers();
}

// Sales
function api_createSale(token, data) {
  if (!validateSession(token)) return authError();
  return createSale(data);
}
function api_getSales(token, year, month) {
  if (!validateSession(token)) return authError();
  return getSales(year, month);
}
function api_getSaleById(token, saleId) {
  if (!validateSession(token)) return authError();
  return getSaleById(saleId);
}
function api_markSaleAsPaid(token, saleId) {
  if (!validateSession(token)) return authError();
  return markSaleAsPaid(saleId);
}
function api_cancelSale(token, saleId, reason) {
  if (!validateSession(token)) return authError();
  return cancelSale(saleId, reason);
}
function api_buildWhatsAppMessage(token, saleId) {
  if (!validateSession(token)) return authError();
  return buildWhatsAppMessage(saleId);
}
function api_sendReceiptByEmail(token, saleId, email) {
  if (!validateSession(token)) return authError();
  return sendReceiptByEmail(saleId, email);
}
function api_regenerateReceiptPdf(token, saleId) {
  if (!validateSession(token)) return authError();
  return generateReceiptPdf(saleId);
}

// Expenses
function api_createExpense(token, data) {
  if (!validateSession(token)) return authError();
  return createExpenseWithAttachment(data);
}
function api_getExpenses(token, year, month) {
  if (!validateSession(token)) return authError();
  return getExpenses(year, month);
}
function api_deleteExpense(token, expenseId) {
  if (!validateSession(token)) return authError();
  return deleteExpense(expenseId);
}

// Private transactions
function api_createPrivateTx(token, data) {
  if (!validateSession(token)) return authError();
  return createPrivateTransaction(data);
}
function api_getPrivateTx(token, year) {
  if (!validateSession(token)) return authError();
  return getPrivateTransactions(year);
}

// Reports
function api_getDashboard(token) {
  if (!validateSession(token)) return authError();
  return getDashboardData();
}
function api_getYearlySummary(token, year) {
  if (!validateSession(token)) return authError();
  return getYearlySummary(year);
}
function api_generateYearlyReport(token, year, notes) {
  if (!validateSession(token)) return authError();
  return generateYearlyClosingReport(year, notes);
}

// Backup / Export
function api_exportSalesCsv(token, year) {
  if (!validateSession(token)) return authError();
  return exportSalesCsv(year);
}
function api_exportExpensesCsv(token, year) {
  if (!validateSession(token)) return authError();
  return exportExpensesCsv(year);
}
function api_exportAll(token, year) {
  if (!validateSession(token)) return authError();
  return exportAllForYear(year);
}
function api_createBackup(token) {
  if (!validateSession(token)) return authError();
  return createFullBackup();
}
function api_getOpenPayments(token) {
  if (!validateSession(token)) return authError();
  return getOpenPayments();
}

function authError() {
  return { success: false, authError: true, error: 'Sessione scaduta. Effettua nuovamente il login.' };
}
