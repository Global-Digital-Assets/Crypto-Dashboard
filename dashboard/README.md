# Crypto Trading Dashboard

## Overview
Real-time crypto trading dashboard displaying live signals from analytics API with service health monitoring.

## Current Deployment
- **Production URL**: http://78.47.150.122:9999
- **VPS**: 78.47.150.122 (Ubuntu)
- **Status**: LIVE & OPERATIONAL

## Architecture
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Backend**: FastAPI (Python)
- **Data Source**: `/api/analysis` endpoint (signal-generator.service)
- **Health Monitoring**: Bot health + Analytics status

## API Endpoints

### Analytics API
- **Primary**: `http://78.47.150.122:8080/api/analysis`
- **Format**: `{symbol, side, proba, tp, sl, timestamp}`
- **Update Frequency**: Every 15 minutes
- **Confidence Levels**: "high" and "ultra" only

### Bot Health
- **Endpoint**: `http://78.47.150.122:8000/health`
- **Purpose**: Monitor trading bot status

## Dashboard Endpoints
- `GET /` - Main dashboard interface
- `GET /api/signals` - Processed trading signals
- `GET /api/status` - System health status
- `GET /api/dashboard-data` - Combined dashboard data

## Signal Processing
1. Reads from `/api/analysis` (single source of truth)
2. Maps `side` → action (buy_long, short, dont_buy_long, dont_short)
3. Converts `proba` → score percentage (0-100%)
4. Filters and sorts by confidence score

## Deployment Notes
- Dashboard server runs on port 9999
- Analytics API on port 8080
- Bot health API on port 8000
- All services run on same VPS for optimal connectivity
- No SSH tunnels required

## Development
```bash
# Install dependencies
pip install fastapi uvicorn httpx jinja2 python-multipart

# Run locally (development)
uvicorn dashboard_server:app --host 0.0.0.0 --port 9999 --reload

# Production deployment on VPS
nohup python3 -m uvicorn dashboard_server:app --host 0.0.0.0 --port 9999 > dashboard.log 2>&1 &
```

## Environment Variables
Copy `.env.example` to `.env` and update values as needed.

---
**Last Updated**: 2025-06-08  
**Status**: Production Ready 
