#!/bin/bash
# Quick script to update N8N_API_TOKEN in .env file

echo "=== N8N API TOKEN UPDATER ==="
echo ""
echo "First, create your token in n8n:"
echo "1. Open: http://localhost:5678"
echo "2. User Icon → Settings → API → Create Token"
echo "3. Copy the token"
echo ""
read -p "Paste your n8n API token here: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "Error: No token provided"
    exit 1
fi

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update token in .env
sed -i.bak "s/N8N_API_TOKEN=.*/N8N_API_TOKEN=$TOKEN/" .env

echo ""
echo "✅ Token updated in .env"
echo "📦 Old .env backed up"
echo ""
echo "Next: Restart the API container:"
echo "docker compose restart api"
