// Database.gs — Spreadsheet initialization and low-level data access.

// ---------------------------------------------------------------------------
// Schema: header rows for each sheet
// ---------------------------------------------------------------------------
var SCHEMAS = {
  Settings: ['key', 'value'],
  Customers: ['customerId', 'name', 'phone', 'email', 'notes', 'createdAt', 'updatedAt'],
  Services: ['serviceId', 'name', 'description', 'defaultPriceCents', 'active', 'createdAt', 'updatedAt'],
  Sales: [
    'saleId', 'receiptNumber', 'date', 'customerId', 'customerNameSnapshot',
    'paymentMethod', 'paymentStatus', 'subtotalCents', 'discountCents', 'tipCents',
    'totalCents', 'notes', 'receiptPdfFileId', 'receiptPdfUrl', 'status', 'createdAt', 'updatedAt'
  ],
  SaleItems: ['saleItemId', 'saleId', 'description', 'quantity', 'unitPriceCents', 'totalCents'],
  Expenses: [
    'expenseId', 'date', 'vendor', 'category', 'amountCents', 'businessPercentage',
    'deductibleAmountCents', 'paymentMethod', 'notes', 'attachmentFileId', 'attachmentUrl',
    'status', 'createdAt', 'updatedAt'
  ],
  PrivateTransactions: ['privateTransactionId', 'date', 'type', 'amountCents', 'notes', 'createdAt', 'updatedAt'],
  DeliveryLogs: ['deliveryLogId', 'saleId', 'channel', 'recipient', 'status', 'errorMessage', 'sentAt'],
  YearClosings: [
    'yearClosingId', 'year', 'revenueCents', 'expenseCents', 'profitCents',
    'privateWithdrawalsCents', 'privateContributionsCents', 'openReceivablesCents',
    'notes', 'pdfFileId', 'pdfUrl', 'createdAt', 'updatedAt'
  ],
  AuditLog: ['auditId', 'entityType', 'entityId', 'action', 'details', 'timestamp']
};

// ---------------------------------------------------------------------------
// Spreadsheet access
// ---------------------------------------------------------------------------
function getSpreadsheet() {
  var props = PropertiesService.getScriptProperties();
  var ssId = props.getProperty('SPREADSHEET_ID');
  if (ssId) {
    try {
      return SpreadsheetApp.openById(ssId);
    } catch (e) {
      // Falls through to create
    }
  }
  // Create new spreadsheet
  var ss = SpreadsheetApp.create(CONFIG.APP_NAME + ' - Database');
  props.setProperty('SPREADSHEET_ID', ss.getId());
  return ss;
}

// ---------------------------------------------------------------------------
// Database initialization
// ---------------------------------------------------------------------------
function initializeDatabase() {
  var ss = getSpreadsheet();

  Object.keys(SCHEMAS).forEach(function(sheetName) {
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.getRange(1, 1, 1, SCHEMAS[sheetName].length)
        .setValues([SCHEMAS[sheetName]])
        .setFontWeight('bold')
        .setBackground('#f5f5f5');
      sheet.setFrozenRows(1);
    }
  });

  // Remove default blank Sheet1 if it still exists
  var defaultSheet = ss.getSheetByName('Sheet1');
  if (defaultSheet && ss.getSheets().length > 1) {
    ss.deleteSheet(defaultSheet);
  }

  // Seed default data on first run
  if (getSettingValue('initialized') !== 'true') {
    seedDefaultSettings();
    seedDefaultServices();
    setSettingValue('initialized', 'true');
  }
}

function seedDefaultSettings() {
  var defaults = {
    businessName: CONFIG.APP_NAME,
    ownerName: '',
    address: '',
    phone: '',
    email: '',
    website: '',
    logoFileId: '',
    vatMode: 'not_registered',
    defaultLanguage: 'it',
    receiptPrefix: '',
    emailEnabled: 'false',
    currency: 'CHF',
    version: CONFIG.VERSION
  };
  Object.keys(defaults).forEach(function(k) {
    setSettingValue(k, defaults[k]);
  });
}

function seedDefaultServices() {
  var now = getCurrentTimestamp();
  CONFIG.DEFAULT_SERVICES.forEach(function(svc) {
    appendRowBySchema(CONFIG.SHEETS.SERVICES, {
      serviceId: generateId(),
      name: svc.name,
      description: svc.description,
      defaultPriceCents: svc.defaultPriceCents,
      active: 'true',
      createdAt: now,
      updatedAt: now
    });
  });
}

// ---------------------------------------------------------------------------
// Generic row operations using SCHEMAS
// ---------------------------------------------------------------------------
function getSheetRows(sheetName) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) return [];
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  var headers = SCHEMAS[sheetName];
  var data = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
  return data.map(function(row) {
    var obj = {};
    headers.forEach(function(h, i) {
      obj[h] = row[i];
    });
    return obj;
  }).filter(function(obj) {
    // Skip completely empty rows
    return Object.values(obj).some(function(v) { return v !== ''; });
  });
}

function appendRowBySchema(sheetName, obj) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error('Sheet not found: ' + sheetName);
  var headers = SCHEMAS[sheetName];
  var row = headers.map(function(h) { return obj[h] !== undefined ? obj[h] : ''; });
  sheet.appendRow(row);
}

function updateRowById(sheetName, idField, idValue, updates) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error('Sheet not found: ' + sheetName);
  var headers = SCHEMAS[sheetName];
  var idColIndex = headers.indexOf(idField);
  if (idColIndex === -1) throw new Error('ID field not found: ' + idField);

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return false;
  var data = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();

  for (var i = 0; i < data.length; i++) {
    if (data[i][idColIndex] === idValue) {
      var rowIndex = i + 2;
      headers.forEach(function(h, j) {
        if (updates.hasOwnProperty(h)) {
          sheet.getRange(rowIndex, j + 1).setValue(updates[h]);
        }
      });
      return true;
    }
  }
  return false;
}

function findRowById(sheetName, idField, idValue) {
  var rows = getSheetRows(sheetName);
  return rows.find(function(r) { return r[idField] === idValue; }) || null;
}

// ---------------------------------------------------------------------------
// Settings helpers
// ---------------------------------------------------------------------------
function getSettings() {
  var rows = getSheetRows(CONFIG.SHEETS.SETTINGS);
  var settings = {};
  rows.forEach(function(r) { settings[r.key] = r.value; });
  return settings;
}

function getSettingValue(key) {
  var rows = getSheetRows(CONFIG.SHEETS.SETTINGS);
  var found = rows.find(function(r) { return r.key === key; });
  return found ? found.value : null;
}

function setSettingValue(key, value) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.SHEETS.SETTINGS);
  if (!sheet) return;
  var lastRow = sheet.getLastRow();
  if (lastRow >= 2) {
    var data = sheet.getRange(2, 1, lastRow - 1, 2).getValues();
    for (var i = 0; i < data.length; i++) {
      if (data[i][0] === key) {
        sheet.getRange(i + 2, 2).setValue(value);
        return;
      }
    }
  }
  sheet.appendRow([key, value]);
}

function saveSettings(settingsObj) {
  Object.keys(settingsObj).forEach(function(k) {
    setSettingValue(k, settingsObj[k]);
  });
  return { success: true };
}

// ---------------------------------------------------------------------------
// Customer helpers
// ---------------------------------------------------------------------------
function getCustomers() {
  return getSheetRows(CONFIG.SHEETS.CUSTOMERS);
}

function upsertCustomer(name, phone, email) {
  if (!name) return null;
  var existing = getSheetRows(CONFIG.SHEETS.CUSTOMERS).find(function(c) {
    return c.name && c.name.toLowerCase() === name.toLowerCase();
  });
  if (existing) return existing.customerId;

  var now = getCurrentTimestamp();
  var id = generateId();
  appendRowBySchema(CONFIG.SHEETS.CUSTOMERS, {
    customerId: id,
    name: sanitizeString(name),
    phone: sanitizeString(phone),
    email: sanitizeString(email),
    notes: '',
    createdAt: now,
    updatedAt: now
  });
  return id;
}

// ---------------------------------------------------------------------------
// Services
// ---------------------------------------------------------------------------
function getServices() {
  return getSheetRows(CONFIG.SHEETS.SERVICES)
    .filter(function(s) { return s.active === 'true' || s.active === true; });
}

function getAllServices() {
  return getSheetRows(CONFIG.SHEETS.SERVICES);
}

function saveService(data) {
  var now = getCurrentTimestamp();
  if (data.serviceId) {
    updateRowById(CONFIG.SHEETS.SERVICES, 'serviceId', data.serviceId, {
      name: sanitizeString(data.name),
      description: sanitizeString(data.description),
      defaultPriceCents: safeInt(data.defaultPriceCents),
      active: data.active ? 'true' : 'false',
      updatedAt: now
    });
    return { success: true, serviceId: data.serviceId };
  }
  var id = generateId();
  appendRowBySchema(CONFIG.SHEETS.SERVICES, {
    serviceId: id,
    name: sanitizeString(data.name),
    description: sanitizeString(data.description),
    defaultPriceCents: safeInt(data.defaultPriceCents),
    active: 'true',
    createdAt: now,
    updatedAt: now
  });
  return { success: true, serviceId: id };
}
