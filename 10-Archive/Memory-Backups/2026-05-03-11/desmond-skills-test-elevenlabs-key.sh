#!/bin/bash
# ElevenLabs API Key Validator
# Tests if the stored API key is valid (returns HTTP 200)

set -e

# Load key from primary vault location
VAULT_ENV="/root/vaults/gentech/.env"
if [[ -f "$VAULT_ENV" ]]; then
  ELEVENLABS_API_KEY=$(grep 'ELEVENLABS_API_KEY' "$VAULT_ENV" | cut -d'=' -f2-)
else
  echo "ERROR: Vault .env not found at $VAULT_ENV"
  exit 1
fi

if [[ -z "$ELEVENLABS_API_KEY" ]] || [[ "$ELEVENLABS_API_KEY" == "***"* ]]; then
  echo "ERROR: API key is masked or empty. Retrieve from ElevenLabs dashboard."
  exit 1
fi

echo "Testing ElevenLabs API key..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/voices)

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✓ Key is valid (HTTP $HTTP_CODE)"
  exit 0
elif [[ "$HTTP_CODE" == "401" ]]; then
  echo "✗ Key is invalid/revoked (HTTP 401). Rotation required."
  exit 401
else
  echo "? Unexpected HTTP code: $HTTP_CODE"
  exit $HTTP_CODE
fi