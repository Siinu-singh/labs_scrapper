#!/bin/bash

# Trigger daily batch scraping
# This script is called by Render's cron job at 2 AM UTC daily

BATCH_SIZE=3
API_URL="https://lab-scraper-api.onrender.com/api/v1/batch/start"

echo "[$(date)] Starting batch trigger..."

# Call the API to start batch scraping
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"batch_size\": $BATCH_SIZE}"

echo "[$(date)] Batch trigger completed"
