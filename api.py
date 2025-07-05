from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import random
import csv
from pathlib import Path
from typing import Optional, List, Dict

app = FastAPI(title="Motivational Quotes API")

templates = Jinja2Templates(directory="templates")

local_quotes = []

def load_local_quotes():
    global local_quotes
    default_quotes = [
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"text": "Life is what happens to you while you're busy making other plans.", "author": "John Lennon"},
        {"text": "You learn more from failure than from success.", "author": "Unknown"},
    ]
    csv_path = Path("sample_quotes_csv.txt")
    if csv_path.exists():
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                local_quotes = list(reader)
        except Exception:
            local_quotes = default_quotes
    else:
        local_quotes = default_quotes

load_local_quotes()

def fetch_public_quotes(limit: int = 50) -> List[Dict]:
    try:
        response = requests.get("https://zenquotes.io/api/quotes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [{"text": item.get('q', ''), "author": item.get('a', 'Unknown')} for item in data[:limit]]
        else:
            response = requests.get(f"https://api.quotable.io/quotes?limit={limit}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{"text": item.get('content', ''), "author": item.get('author', 'Unknown')} for item in data.get('results', [])]
    except Exception:
        pass
    return []

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/quotes/random")
async def get_random_quote(source: str = Query("public")):
    if source == "local":
        quotes = local_quotes.copy()
    else:
        quotes = fetch_public_quotes(50)
        if not quotes:
            return {"error": "Unable to fetch quotes from public API. Try again later or use local quotes."}

    random_quote = random.choice(quotes)
    return random_quote
