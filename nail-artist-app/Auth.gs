// Auth.gs — PIN authentication and session management.

// ---------------------------------------------------------------------------
// PIN management
// ---------------------------------------------------------------------------
function isPinSet() {
  var props = PropertiesService.getScriptProperties();
  return !!props.getProperty('PIN_HASH');
}

function setPin(rawPin) {
  if (!rawPin || rawPin.toString().length < 4) {
    return { success: false, error: 'Il PIN deve avere almeno 4 cifre.' };
  }
  var props = PropertiesService.getScriptProperties();
  props.setProperty('PIN_HASH', hashPin(rawPin.toString()));
  return { success: true };
}

function verifyPin(rawPin) {
  var props = PropertiesService.getScriptProperties();
  var stored = props.getProperty('PIN_HASH');
  if (!stored) {
    // First run: accept default PIN and set it
    if (rawPin.toString() === CONFIG.DEFAULT_PIN) {
      props.setProperty('PIN_HASH', hashPin(CONFIG.DEFAULT_PIN));
      return { success: true, firstRun: true, sessionToken: createSession() };
    }
    return { success: false, error: 'PIN non impostato. Usa il PIN predefinito: ' + CONFIG.DEFAULT_PIN };
  }
  if (hashPin(rawPin.toString()) === stored) {
    return { success: true, sessionToken: createSession() };
  }
  return { success: false, error: 'PIN errato. Riprova.' };
}

function changePin(currentPin, newPin) {
  var check = verifyPin(currentPin);
  if (!check.success) return { success: false, error: 'PIN attuale errato.' };
  return setPin(newPin);
}

// ---------------------------------------------------------------------------
// Session management (tokens stored in UserCache, expire with timeout)
// ---------------------------------------------------------------------------
function createSession() {
  var token = Utilities.getUuid();
  var cache = CacheService.getUserCache();
  cache.put('SESSION_TOKEN', token, CONFIG.SESSION_TIMEOUT_SECONDS);
  return token;
}

function validateSession(token) {
  if (!token) return false;
  var cache = CacheService.getUserCache();
  var stored = cache.get('SESSION_TOKEN');
  return stored && stored === token;
}

function logout(token) {
  var cache = CacheService.getUserCache();
  cache.remove('SESSION_TOKEN');
  return { success: true };
}

// ---------------------------------------------------------------------------
// Initialization check (called on app open)
// ---------------------------------------------------------------------------
function getAppInitStatus() {
  var props = PropertiesService.getScriptProperties();
  try {
    // Ensure DB and folders are ready
    initializeDatabase();
    initializeFolders();
  } catch (e) {
    Logger.log('Init error: ' + e.message);
    return { ready: false, error: e.message };
  }
  return {
    ready: true,
    pinSet: isPinSet(),
    defaultPin: isPinSet() ? null : CONFIG.DEFAULT_PIN,
    businessName: getSettingValue('businessName') || CONFIG.APP_NAME
  };
}
