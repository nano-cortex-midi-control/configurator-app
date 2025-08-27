#!/bin/bash

# Test script za MIDI Configurator API
echo "=== MIDI Configurator API Test ==="

BASE_URL="http://localhost:5001/api"

echo "1. Testiranje health check..."
curl -s "$BASE_URL/health" | python3 -m json.tool

echo -e "\n2. Dohvatanje komandi..."
curl -s "$BASE_URL/commands" | python3 -m json.tool

echo -e "\n3. Kreiranje nove komande..."
curl -s -X POST "$BASE_URL/commands" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test komanda", "value": 42}' | python3 -m json.tool

echo -e "\n4. Dohvatanje komandi nakon dodavanja..."
curl -s "$BASE_URL/commands" | python3 -m json.tool

echo -e "\n5. Dohvatanje mapiranja tastera..."
curl -s "$BASE_URL/button-mappings" | python3 -m json.tool

echo -e "\n6. Testiranje USB portova..."
curl -s "$BASE_URL/usb-ports" | python3 -m json.tool

echo -e "\n✅ API test completed!"
