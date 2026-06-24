// Config.gs — Application constants. Change FOLDER_NAMES.ROOT to match your business name.

var CONFIG = {
  APP_NAME: 'Mary Jo Nails',
  APP_SUBTITLE: 'Contabilità',
  VERSION: '1.0.0',
  CURRENCY: 'CHF',
  LOCALE: 'it-CH',
  TIMEZONE: 'Europe/Zurich',

  SHEETS: {
    SETTINGS: 'Settings',
    CUSTOMERS: 'Customers',
    SERVICES: 'Services',
    SALES: 'Sales',
    SALE_ITEMS: 'SaleItems',
    EXPENSES: 'Expenses',
    PRIVATE_TRANSACTIONS: 'PrivateTransactions',
    DELIVERY_LOGS: 'DeliveryLogs',
    YEAR_CLOSINGS: 'YearClosings',
    AUDIT_LOG: 'AuditLog'
  },

  PAYMENT_METHODS: ['Contanti', 'TWINT', 'Carta', 'Bonifico', 'Altro'],
  PAYMENT_STATUSES: ['Pagato', 'Aperto', 'Pagato parzialmente'],

  EXPENSE_CATEGORIES: [
    'Prodotti unghie / materiale',
    'Attrezzi e apparecchi',
    'Affitto / studio',
    'Marketing / social media / sito web',
    'Telefono / internet',
    'Corsi / formazione',
    'Assicurazioni',
    'Commissioni banca / TWINT / carta',
    'Trasporti',
    'Materiale ufficio',
    'Altro'
  ],

  DEFAULT_SERVICES: [
    { name: 'Semipermanente mani', description: 'Smalto semipermanente sulle mani', defaultPriceCents: 4500 },
    { name: 'Refill gel', description: 'Riempimento gel esistente', defaultPriceCents: 5500 },
    { name: 'Ricostruzione gel', description: 'Ricostruzione completa in gel', defaultPriceCents: 7000 },
    { name: 'Nail art', description: 'Decorazioni nail art', defaultPriceCents: 1500 },
    { name: 'Pedicure', description: 'Trattamento pedicure', defaultPriceCents: 5000 },
    { name: 'Rimozione', description: 'Rimozione gel / semipermanente', defaultPriceCents: 2000 },
    { name: 'Riparazione unghia', description: 'Riparazione singola unghia', defaultPriceCents: 800 }
  ],

  FOLDER_NAMES: {
    ROOT: 'Mary Jo Nails - Contabilità',
    RECEIPTS: 'Ricevute',
    EXPENSES_FOLDER: 'Spese',
    YEAR_CLOSING: 'Jahresabschluss',
    BACKUP: 'Backup',
    EXPORT: 'Export'
  },

  // Revenue thresholds for Swiss regulations (in cents)
  MWST_THRESHOLD_CENTS: 10000000,   // CHF 100'000 — MWST registration may be required
  ORDINARY_ACCOUNTING_THRESHOLD_CENTS: 50000000,  // CHF 500'000 — ordinary accounting

  SESSION_TIMEOUT_SECONDS: 28800,   // 8 hours
  DEFAULT_PIN: '1234',

  // Receipt number format: YYYY-NNNN
  RECEIPT_NUMBER_DIGITS: 4
};
