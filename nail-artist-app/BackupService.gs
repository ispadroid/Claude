// BackupService.gs — CSV exports, JSON backup.

// ---------------------------------------------------------------------------
// CSV helpers
// ---------------------------------------------------------------------------
function arrayToCsv(headers, rows) {
  var lines = [headers.join(',')];
  rows.forEach(function(r) {
    var line = headers.map(function(h) {
      var v = r[h] !== undefined ? r[h] : '';
      v = v.toString().replace(/"/g, '""');
      if (v.includes(',') || v.includes('"') || v.includes('\n')) {
        v = '"' + v + '"';
      }
      return v;
    });
    lines.push(line.join(','));
  });
  return lines.join('\n');
}

function saveCsvToExport(csvContent, fileName, year) {
  var folder = getExportFolder(year || getCurrentYear());
  var blob = Utilities.newBlob(csvContent, MimeType.CSV, fileName);
  var file = folder.createFile(blob);
  return { fileId: file.getId(), url: file.getUrl(), name: fileName };
}

// ---------------------------------------------------------------------------
// Export functions
// ---------------------------------------------------------------------------
function exportSalesCsv(year) {
  var rows = getSales(year);
  var headers = SCHEMAS.Sales;
  // Add human-readable money columns
  var enriched = rows.map(function(r) {
    return Object.assign({}, r, {
      totalCents: formatMoneyPlain(r.totalCents),
      subtotalCents: formatMoneyPlain(r.subtotalCents),
      discountCents: formatMoneyPlain(r.discountCents),
      tipCents: formatMoneyPlain(r.tipCents)
    });
  });
  var csv = arrayToCsv(headers, enriched);
  var fileName = 'Vendite_' + (year || getCurrentYear()) + '.csv';
  return saveCsvToExport(csv, fileName, year);
}

function exportSaleItemsCsv(year) {
  var sales = getSales(year);
  var saleIds = new Set(sales.map(function(s) { return s.saleId; }));
  var rows = getSheetRows(CONFIG.SHEETS.SALE_ITEMS)
    .filter(function(i) { return saleIds.has(i.saleId); });
  var headers = SCHEMAS.SaleItems;
  var csv = arrayToCsv(headers, rows);
  var fileName = 'DettaglioVendite_' + (year || getCurrentYear()) + '.csv';
  return saveCsvToExport(csv, fileName, year);
}

function exportExpensesCsv(year) {
  var rows = getExpenses(year);
  var headers = SCHEMAS.Expenses;
  var csv = arrayToCsv(headers, rows);
  var fileName = 'Spese_' + (year || getCurrentYear()) + '.csv';
  return saveCsvToExport(csv, fileName, year);
}

function exportPrivateTransactionsCsv(year) {
  var rows = getPrivateTransactions(year);
  var headers = SCHEMAS.PrivateTransactions;
  var csv = arrayToCsv(headers, rows);
  var fileName = 'Transazioni_Private_' + (year || getCurrentYear()) + '.csv';
  return saveCsvToExport(csv, fileName, year);
}

// ---------------------------------------------------------------------------
// Full JSON backup
// ---------------------------------------------------------------------------
function createFullBackup() {
  var year = getCurrentYear();
  var backup = {
    exportedAt: getCurrentTimestamp(),
    appVersion: CONFIG.VERSION,
    year: year,
    data: {}
  };

  Object.keys(SCHEMAS).forEach(function(sheetName) {
    if (sheetName !== 'AuditLog') {  // skip audit log for size
      backup.data[sheetName] = getSheetRows(sheetName);
    }
  });

  var json = JSON.stringify(backup, null, 2);
  var folder = getBackupFolder(year);
  var fileName = 'Backup_' + Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyyMMdd_HHmm') + '.json';
  var blob = Utilities.newBlob(json, MimeType.PLAIN_TEXT, fileName);
  var file = folder.createFile(blob);

  writeAuditLog('System', 'backup', 'created', { fileName: fileName, size: json.length });
  return { success: true, fileId: file.getId(), url: file.getUrl(), name: fileName };
}

// ---------------------------------------------------------------------------
// Combined yearly export (all CSVs)
// ---------------------------------------------------------------------------
function exportAllForYear(year) {
  var results = {};
  try { results.sales = exportSalesCsv(year); } catch (e) { results.salesError = e.message; }
  try { results.saleItems = exportSaleItemsCsv(year); } catch (e) { results.saleItemsError = e.message; }
  try { results.expenses = exportExpensesCsv(year); } catch (e) { results.expensesError = e.message; }
  try { results.privateTx = exportPrivateTransactionsCsv(year); } catch (e) { results.privateTxError = e.message; }
  return { success: true, year: year, files: results };
}
