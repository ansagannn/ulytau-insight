# Ulytau Inside AI Agent

AI-powered news monitoring agent for the Ulytau region (Kazakhstan).
Monitors major news sources, filters for local relevance, detects legislative changes, and generates AI summaries.

## Features
- **RSS Monitoring**: Aggregates news from TengriNews, Zakon.kz, Informburo, Gov.kz.
- **Region Filtering**: Only selects news relevant to Ulytau, Zhezkazgan, Satpayev.
- **Law Detection**: Identifies laws, decrees, and orders (заң, қаулы, etc.).
- **AI Summarization**: Generates short, journalistic insights using NLP models.
- **API**: FastAPI backend providing clean JSON output.
- **Telegram Bot**: Interactive bot with commands and auto-posting capabilities.

## Project Structure
```
ulytau-insight/
├── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── rss_parser.py    # Core logic: fetch, filter, process
│   ├── rss_sources.py   # Config: URLs and keywords
│   ├── law_detector.py  # Law keyword detection
│   ├── summarizer.py    # AI summarization (Transformers)
│   └── telegram_bot.py  # Telegram Bot implementation
├── requirements.txt
└── README.md
```

## Setup & Run

### 1. Prerequisites
- Python 3.9+ installed
- Internet connection (to fetch RSS and download ML models)

### 2. Install Dependencies
Navigate to the project directory:
```bash
cd ulytau-insight
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the `ulytau-insight` directory (see `.env.example`).
```ini
BOT_TOKEN=your_token_here
API_URL=http://127.0.0.1:8000/news
CHAT_ID=your_channel_id  # Optional: for auto-posting
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```
*Note: The first run might take a few seconds to download the summarization model.*

### 5. Run the Telegram Bot
Open a new terminal and run:
```bash
python app/telegram_bot.py
```
> **Render.com Note**: If deploying to Render, ensure dependencies are installed via `pip install -r requirements.txt`. The `python-telegram-bot[job-queue]` extra is required for the internal scheduler. The bot now includes a fallback to `asyncio` if this is missing, but full installation is recommended.

### 6. Usage
**API**:
- Check status: `http://127.0.0.1:8000/`
- Get news: `http://127.0.0.1:8000/news`

**Telegram Bot**:
- `/start` - Start bot
- `/latest` - Get latest news
- `/laws` - Get latest laws
- `/search <text>` - Search news

## API Response Example
```json
{
  "count": 1,
  "data": [
    {
      "title": "Новые проекты в области энергетики Жезказгана",
      "summary": "В Жезказгане утвержден план модернизации ТЭЦ...",
      "type": "news",
      "source": "Zakon.kz",
      "link": "https://zakon.kz/..."
    }
  ]
}
```
