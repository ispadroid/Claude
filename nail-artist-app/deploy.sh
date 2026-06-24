#!/bin/bash
# deploy.sh — One-time setup and deployment for Mary Jo Nails Contabilità
# Run this script from the nail-artist-app/ folder on your own computer.
# Requirements: Node.js >= 16, internet connection, Google Account

set -e

echo ""
echo "💅 Mary Jo Nails — Contabilità Deployment"
echo "==========================================="
echo ""

# 1. Install clasp if not present
if ! command -v clasp &> /dev/null; then
  echo "📦 Installing @google/clasp..."
  npm install -g @google/clasp
else
  echo "✅ clasp already installed ($(clasp --version))"
fi

# 2. Login if not authenticated
if [ ! -f "$HOME/.clasprc.json" ]; then
  echo ""
  echo "🔑 Google Login required (browser will open)..."
  clasp login
else
  echo "✅ Already logged in to Google"
fi

# 3. Create new Apps Script project
echo ""
echo "📝 Creating new Apps Script project..."
clasp create --title "Mary Jo Nails - Contabilità" --type webapp

# 4. Push all files
echo ""
echo "⬆️  Uploading all files to Google Apps Script..."
clasp push --force

echo ""
echo "✅ Upload complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Run: clasp open"
echo "      → Opens the Apps Script editor in your browser"
echo "   2. In the editor: Click 'Deploy' → 'New deployment'"
echo "      → Type: Web App"
echo "      → Execute as: Me"
echo "      → Who has access: Only myself"
echo "   3. Click 'Deploy' → copy the Web App URL"
echo "   4. Open that URL on your iPhone Safari"
echo "   5. Safari → Share → 'Add to Home Screen'"
echo ""
echo "🔐 Default PIN: 1234  — Change it immediately in Settings!"
echo ""
