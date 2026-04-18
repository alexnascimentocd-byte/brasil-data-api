#!/bin/bash
# keep_alive.sh — Pings API to prevent Render free tier sleep
# Run via cron: */14 * * * * bash /root/brasil-data-api/keep_alive.sh

URL="https://brasil-data-api.onrender.com/health"

if curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null | grep -q "200"; then
    echo "$(date): API alive ✅"
else
    echo "$(date): API sleeping or down ❌ — ping to wake up"
    curl -s "$URL" >/dev/null 2>&1
fi
