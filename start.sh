#!/bin/bash

# Default PORT is 8000 if not set (for local dev)
PORT="${PORT:-8000}"

# Start URI API in background
# Render (and others) bind external traffic to 0.0.0.0:$PORT
echo "🚀 Starting API on port $PORT..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT &

# Wait for API to spin up
sleep 5

# Set API_URL for the bot so it knows where to find the local API
# 127.0.0.1 is safe here because they run in the same container
export API_URL="http://127.0.0.1:$PORT"

echo "🤖 Starting Telegram Bot connecting to $API_URL..."

# Start Telegram Bot in foreground
python app/telegram_bot.py
