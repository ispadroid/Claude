// DriveService.gs — Google Drive folder management and file operations.

function getRootFolder() {
  var props = PropertiesService.getScriptProperties();
  var folderId = props.getProperty('ROOT_FOLDER_ID');
  if (folderId) {
    try {
      return DriveApp.getFolderById(folderId);
    } catch (e) { /* fall through */ }
  }
  // Create root folder
  var folder = DriveApp.createFolder(CONFIG.FOLDER_NAMES.ROOT);
  props.setProperty('ROOT_FOLDER_ID', folder.getId());
  return folder;
}

function getOrCreateSubfolder(parent, name) {
  var iter = parent.getFoldersByName(name);
  if (iter.hasNext()) return iter.next();
  return parent.createFolder(name);
}

function initializeFolders() {
  var root = getRootFolder();
  var props = PropertiesService.getScriptProperties();

  var folderMap = {
    RECEIPTS_FOLDER_ID: CONFIG.FOLDER_NAMES.RECEIPTS,
    EXPENSES_FOLDER_ID: CONFIG.FOLDER_NAMES.EXPENSES_FOLDER,
    YEAR_CLOSING_FOLDER_ID: CONFIG.FOLDER_NAMES.YEAR_CLOSING,
    BACKUP_FOLDER_ID: CONFIG.FOLDER_NAMES.BACKUP,
    EXPORT_FOLDER_ID: CONFIG.FOLDER_NAMES.EXPORT
  };

  var result = {};
  Object.keys(folderMap).forEach(function(propKey) {
    var name = folderMap[propKey];
    var storedId = props.getProperty(propKey);
    if (storedId) {
      try {
        DriveApp.getFolderById(storedId);
        result[propKey] = storedId;
        return;
      } catch (e) { /* recreate */ }
    }
    var folder = getOrCreateSubfolder(root, name);
    props.setProperty(propKey, folder.getId());
    result[propKey] = folder.getId();
  });
  return result;
}

function getYearSubfolder(parentPropKey, year) {
  var props = PropertiesService.getScriptProperties();
  var parentId = props.getProperty(parentPropKey);
  if (!parentId) {
    initializeFolders();
    parentId = props.getProperty(parentPropKey);
  }
  var parent = DriveApp.getFolderById(parentId);
  return getOrCreateSubfolder(parent, year.toString());
}

function saveFileToDrive(blob, fileName, folderId) {
  var folder = DriveApp.getFolderById(folderId);
  var file = folder.createFile(blob.setName(fileName));
  return {
    fileId: file.getId(),
    url: file.getUrl(),
    name: file.getName()
  };
}

function getReceiptsFolder(year) {
  return getYearSubfolder('RECEIPTS_FOLDER_ID', year);
}

function getExpensesFolder(year) {
  return getYearSubfolder('EXPENSES_FOLDER_ID', year);
}

function getYearClosingFolder(year) {
  return getYearSubfolder('YEAR_CLOSING_FOLDER_ID', year);
}

function getBackupFolder(year) {
  return getYearSubfolder('BACKUP_FOLDER_ID', year);
}

function getExportFolder(year) {
  return getYearSubfolder('EXPORT_FOLDER_ID', year);
}

function getDriveFolderUrl(folderId) {
  try {
    return DriveApp.getFolderById(folderId).getUrl();
  } catch (e) {
    return '';
  }
}

// Upload expense attachment from base64 data URI
function saveExpenseAttachment(base64Data, mimeType, fileName, year) {
  try {
    var bytes = Utilities.base64Decode(base64Data.split(',').pop());
    var blob = Utilities.newBlob(bytes, mimeType, fileName);
    var folder = getExpensesFolder(year);
    var file = folder.createFile(blob);
    return { fileId: file.getId(), url: file.getUrl() };
  } catch (e) {
    Logger.log('saveExpenseAttachment error: ' + e.message);
    return { fileId: '', url: '' };
  }
}
