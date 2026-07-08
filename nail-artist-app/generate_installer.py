#!/usr/bin/env python3
"""Generates Installer.gs — a self-contained Apps Script installer that
deploys the complete Mary Jo Nails app into the current GAS project."""

import json
import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Files to embed, in order. Tuples: (filename, type, name_in_gas)
FILES = [
    ('appsscript.json',    'JSON',       'appsscript'),
    ('Config.gs',          'SERVER_JS',  'Config'),
    ('Utils.gs',           'SERVER_JS',  'Utils'),
    ('Database.gs',        'SERVER_JS',  'Database'),
    ('DriveService.gs',    'SERVER_JS',  'DriveService'),
    ('Auth.gs',            'SERVER_JS',  'Auth'),
    ('Sales.gs',           'SERVER_JS',  'Sales'),
    ('Expenses.gs',        'SERVER_JS',  'Expenses'),
    ('Reports.gs',         'SERVER_JS',  'Reports'),
    ('PdfService.gs',      'SERVER_JS',  'PdfService'),
    ('EmailService.gs',    'SERVER_JS',  'EmailService'),
    ('BackupService.gs',   'SERVER_JS',  'BackupService'),
    ('Code.gs',            'SERVER_JS',  'Code'),
    ('Styles.html',        'HTML',       'Styles'),
    ('JavaScript.html',    'HTML',       'JavaScript'),
    ('Index.html',         'HTML',       'Index'),
]

def main():
    gas_files = []
    total_bytes = 0
    for filename, file_type, gas_name in FILES:
        path = os.path.join(APP_DIR, filename)
        if not os.path.exists(path):
            print(f'WARNING: {filename} not found, skipping')
            continue
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        total_bytes += len(source)
        gas_files.append({'name': gas_name, 'type': file_type, 'source': source})
        print(f'  ✓ {filename} ({len(source):,} bytes)')

    payload = json.dumps({'files': gas_files}, ensure_ascii=False)
    payload_js = json.dumps(payload)  # double-encoded string for embedding in JS

    print(f'\n  Total source: {total_bytes:,} bytes across {len(gas_files)} files')
    print(f'  Installer payload: {len(payload_js):,} bytes')

    installer = f'''// Installer.gs — Mary Jo Nails Contabilità
// ============================================================
// ISTRUZIONI (mobile-friendly):
//
//  1. Apri script.google.com → Nuovo progetto
//  2. Nomina il progetto "Mary Jo Nails - Contabilità"
//  3. ⚙️ Impostazioni progetto → spunta "appsscript.json"
//  4. Clicca su appsscript.json → incolla il contenuto di
//     installer_appsscript.json (file nella stessa cartella del repo)
//  5. Clicca su Code.gs → cancella tutto → incolla questo file
//  6. Clicca "Salva" (icona disco o Ctrl+S)
//  7. Clicca "Esegui" → seleziona "install" → Autorizza
//  8. Aspetta ~30 secondi → ✅ Fatto!
//  9. Ricarica la pagina — tutti i file appaiono nel progetto
// 10. Deploy → Nuova distribuzione → App web
//     • "Esegui come": Me (tu)
//     • "Chi ha accesso": Solo io
// 11. Copia il Web App URL → apri su iPhone → Aggiungi a Home
// ============================================================

var INSTALLER_PAYLOAD = {payload_js};

function install() {{
  var ui;
  try {{ ui = SpreadsheetApp.getUi(); }} catch(e) {{}}

  try {{
    var scriptId = ScriptApp.getScriptId();
    var token = ScriptApp.getOAuthToken();

    Logger.log('Installing to project: ' + scriptId);
    Logger.log('Payload size: ' + INSTALLER_PAYLOAD.length + ' bytes');

    var response = UrlFetchApp.fetch(
      'https://script.googleapis.com/v1/projects/' + scriptId + '/content',
      {{
        method: 'PUT',
        headers: {{
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json; charset=utf-8'
        }},
        payload: INSTALLER_PAYLOAD,
        muteHttpExceptions: true
      }}
    );

    var code = response.getResponseCode();
    var body = response.getContentText();
    Logger.log('Response ' + code + ': ' + body.substring(0, 300));

    if (code === 200) {{
      Browser.msgBox(
        '✅ Installazione completata!',
        '🎉 Tutti i file sono stati caricati!\\n\\n' +
        'Prossimi passi:\\n' +
        '1. Ricarica questa pagina (F5)\\n' +
        '2. Deploy → Nuova distribuzione → App web\\n' +
        '3. Esegui come: Me  /  Accesso: Solo io\\n' +
        '4. Copia il Web App URL\\n' +
        '5. Apri su iPhone → Safari → Aggiungi a Home Screen\\n\\n' +
        'PIN predefinito: 1234 — cambialo subito!',
        Browser.Buttons.OK
      );
    }} else {{
      var errMsg = body.substring(0, 600);
      Browser.msgBox(
        '❌ Errore ' + code,
        'Dettagli:\\n' + errMsg + '\\n\\nControlla il log (Visualizza → Log esecuzioni).',
        Browser.Buttons.OK
      );
    }}
  }} catch(e) {{
    Logger.log('Install error: ' + e.message + '\\n' + e.stack);
    Browser.msgBox(
      '❌ Errore installazione',
      e.message + '\\n\\nAssicurati di aver aggiornato appsscript.json con installer_appsscript.json prima di eseguire.',
      Browser.Buttons.OK
    );
  }}
}}
'''

    out_path = os.path.join(APP_DIR, 'Installer.gs')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(installer)
    print(f'\n✅ Written: Installer.gs ({os.path.getsize(out_path):,} bytes)')

if __name__ == '__main__':
    main()
