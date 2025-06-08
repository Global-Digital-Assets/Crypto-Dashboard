from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging
import traceback
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

# Enable CORS for all origins (preview use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CONFIGURATION
ANALYTICS_API = os.getenv("ANALYTICS_API", "http://78.47.150.122:8080/api/analysis")
ANALYTICS_HEALTH = "http://78.47.150.122:8080/api/status"
BOT_HEALTH = os.getenv("BOT_HEALTH", "http://78.47.150.122:8000/health")
TOKENS = [
    'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'XRP', 'DOT', 'LINK', 'AVAX', 'ATOM',
    'TRX', 'LTC', 'FIL', 'DOGE', 'MATIC', 'SHIB', 'PEPE', 'GMT', 'SAND', 'AAVE',
    'NEAR', 'FTM', 'UNI', 'OP', 'ARB', 'INJ', 'RNDR', 'SEI', 'TIA', 'WIF'
]

# --- Data Fetching Logic ---
async def fetch_signals() -> List[Dict[str, Any]]:
    headers = {
        "User-Agent": "Dashboard/1.0",
        "Accept": "application/json",
        "Connection": "close"
    }
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        try:
            logger.info(f"Fetching signals from: {ANALYTICS_API}")
            response = await client.get(ANALYTICS_API)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            raw_data = response.json()
            logger.info(f"Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
            extracted = extract_list(raw_data)
            logger.info(f"Extracted {len(extracted)} signals")
            return extracted
        except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            logger.error(f"Timeout fetching signals: {type(e).__name__}")
            return []
        except Exception as e:
            logger.error(f"Error fetching signals: {type(e).__name__}: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

# --- Signal Processing ---
def extract_list(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, dict):
        # First priority: 'signals' key (new format)
        signals = raw.get('signals')
        if isinstance(signals, list):
            return signals
        # Second priority: 'opportunities' key (old format)
        opportunities = raw.get('opportunities')
        if isinstance(opportunities, list):
            return opportunities
        # Third priority: 'data' key
        data = raw.get('data')
        if isinstance(data, list):
            return data
        # fallback: first list value
        for v in raw.values():
            if isinstance(v, list):
                return v
        return []
    if isinstance(raw, list):
        return raw
    return []

def process_signals(raw_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Extract the actual signals list from API response
    signals_list = extract_list(raw_signals)
    signal_map = {s['symbol']: s for s in signals_list}
    results = []
    for token in TOKENS:
        symbol = f"{token}USDT"
        if symbol in signal_map:
            signal = signal_map[symbol]
            # Map 'side' to action, 'proba' to score percentage
            side = signal.get('side', '').lower()
            action = side if side in ['buy_long', 'short', 'dont_buy_long', 'dont_short'] else 'NO_SIGNAL'
            
            # Convert probability to percentage score (0-100)
            proba = signal.get('proba', 0)
            score = int(round(proba * 100)) if proba <= 1 else int(round(proba))
            
            results.append({
                'symbol': token,
                'action': action,
                'score': score,
                'timestamp': signal.get('timestamp', None),
                'tp': signal.get('tp'),  # Take profit
                'sl': signal.get('sl')   # Stop loss
            })
        else:
            results.append({
                'symbol': token,
                'action': 'NO_SIGNAL',
                'score': 0,
                'timestamp': None,
                'tp': None,
                'sl': None
            })
    return sorted(results, key=lambda x: x['score'], reverse=True)


# --- Utility ---
def parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        # Accepts ISO8601 or '%Y-%m-%d %H:%M:%S' style
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        try:
            return datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return None

# --- Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def safe_api_status():
    try:
        # Get bot health and signals
        bot_status = await check_health(BOT_HEALTH)
        raw_signals = await fetch_signals()
        
        # Analytics is UP if we successfully get signals
        analytics_status = len(raw_signals) > 0
        
        # Use current timestamp as last update
        now = datetime.now(timezone.utc)
        last_signal_ts = now.isoformat()
        
        # Get the latest signal timestamp if available
        latest_signal_time = None
        if raw_signals:
            for signal in raw_signals:
                if isinstance(signal, dict) and 'timestamp' in signal and signal['timestamp']:
                    latest_signal_time = signal['timestamp']
                    last_signal_ts = latest_signal_time
                    break
        
        # Calculate candle freshness based on analytics timestamp  
        candle_active = analytics_status
        age_seconds = 0
        
        if latest_signal_time:
            try:
                signal_time = parse_timestamp(latest_signal_time)
                if signal_time:
                    age_seconds = (now - signal_time).total_seconds()
                    candle_active = age_seconds < 900  # 15 minutes
            except:
                pass
                
        return {
            "buying_bot_status": "UP" if bot_status else "DOWN",
            "analytics_status": "UP" if analytics_status else "DOWN", 
            "last_signal_timestamp": last_signal_ts,
            "candle_update_active": candle_active,
            "candle_age_seconds": age_seconds
        }
    except Exception as e:
        logger.error(f"api_status error: {e}")
        now = datetime.now(timezone.utc)
        return {
            "buying_bot_status": "DOWN",
            "analytics_status": "DOWN",
            "last_signal_timestamp": now.isoformat(),
            "candle_update_active": False,
            "candle_age_seconds": None
        }

@app.get("/api/signals")
async def safe_api_signals():
    try:
        logger.info("safe_api_signals: Starting")
        signals_list = await fetch_signals()
        logger.info(f"safe_api_signals: Got {len(signals_list)} raw signals")
        processed = process_signals(signals_list)
        logger.info(f"safe_api_signals: Processed to {len(processed)} signals")
        return processed
    except Exception as e:
        logger.error(f"api_signals error: {e}")
        logger.error(f"api_signals traceback: {traceback.format_exc()}")
        # Return NO_SIGNAL defaults
        return [ {"symbol": t, "action": "NO_SIGNAL", "score": 0, "timestamp": None, "tp": None, "sl": None} for t in TOKENS ]

@app.get("/api/dashboard-data")
async def api_dashboard_data():
    try:
        status_task = asyncio.create_task(safe_api_status())
        signals_task = asyncio.create_task(safe_api_signals())
        status = await status_task
        signals = await signals_task
        return {"status": status, "signals": signals}
    except Exception as e:
        err = traceback.format_exc()
        logger.error(f"api_dashboard_data error: {e}\n{err}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": err}
        )

# Debug exception handler to return stack trace
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "trace": traceback.format_exc()
        }
    )

async def check_health(url: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=3)
            return resp.status_code == 200
    except Exception:
        return False
