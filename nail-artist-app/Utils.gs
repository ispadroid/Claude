// Utils.gs — Shared utility functions.

function generateId() {
  return Utilities.getUuid();
}

function hashPin(pin) {
  var bytes = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    pin.toString()
  );
  return bytes.map(function(b) {
    var hex = (b & 0xff).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}

function formatMoney(cents) {
  if (cents === null || cents === undefined || isNaN(cents)) return 'CHF 0.00';
  var amount = Math.round(parseInt(cents)) / 100;
  return 'CHF ' + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, "'");
}

function formatMoneyPlain(cents) {
  if (cents === null || cents === undefined || isNaN(cents)) return '0.00';
  return (Math.round(parseInt(cents)) / 100).toFixed(2);
}

function parseCents(value) {
  if (value === null || value === undefined || value === '') return 0;
  var str = value.toString().replace(/[^0-9.,\-]/g, '').replace(',', '.');
  return Math.round(parseFloat(str) * 100) || 0;
}

function formatDate(date) {
  if (!date) return '';
  var d = (date instanceof Date) ? date : new Date(date);
  return Utilities.formatDate(d, CONFIG.TIMEZONE, 'dd.MM.yyyy');
}

function formatDateTime(date) {
  if (!date) return '';
  var d = (date instanceof Date) ? date : new Date(date);
  return Utilities.formatDate(d, CONFIG.TIMEZONE, 'dd.MM.yyyy HH:mm');
}

function formatDateISO(date) {
  if (!date) return '';
  var d = (date instanceof Date) ? date : new Date(date);
  return Utilities.formatDate(d, CONFIG.TIMEZONE, 'yyyy-MM-dd');
}

function getCurrentYear() {
  return parseInt(Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyy'));
}

function getCurrentMonth() {
  return parseInt(Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'MM'));
}

function getCurrentTimestamp() {
  return new Date().toISOString();
}

function padReceiptNumber(n) {
  var s = n.toString();
  while (s.length < CONFIG.RECEIPT_NUMBER_DIGITS) s = '0' + s;
  return s;
}

function buildReceiptNumber(year, seq) {
  return year + '-' + padReceiptNumber(seq);
}

function writeAuditLog(entityType, entityId, action, details) {
  try {
    var row = {
      auditId: generateId(),
      entityType: entityType,
      entityId: entityId,
      action: action,
      details: typeof details === 'object' ? JSON.stringify(details) : String(details || ''),
      timestamp: getCurrentTimestamp()
    };
    appendRowBySchema(CONFIG.SHEETS.AUDIT_LOG, row);
  } catch (e) {
    Logger.log('AuditLog error: ' + e.message);
  }
}

function sanitizeString(s) {
  if (!s) return '';
  return s.toString().trim();
}

function safeInt(v) {
  var n = parseInt(v);
  return isNaN(n) ? 0 : n;
}
