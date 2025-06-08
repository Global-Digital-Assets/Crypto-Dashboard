#!/usr/bin/env python3
"""
Simple proxy server to fetch analytics data via SSH and serve it locally
"""
import subprocess
import json
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/api/analysis")
async def proxy_analysis():
    """Proxy the analytics API via SSH command"""
    try:
        # Use SSH to fetch data from the VPS
        cmd = [
            'ssh', '-i', '../binance_key', 
            '-o', 'ConnectTimeout=10',
            '-o', 'StrictHostKeyChecking=no',
            'root@78.47.150.122',
            'curl -s http://localhost:8080/api/analysis'
        ]
        
        logger.info("Fetching data via SSH...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            logger.info(f"Successfully fetched data with {len(data.get('opportunities', []))} opportunities")
            return data
        else:
            logger.error(f"SSH command failed: {result.stderr}")
            return {"error": "SSH fetch failed", "opportunities": []}
            
    except subprocess.TimeoutExpired:
        logger.error("SSH command timed out")
        return {"error": "Timeout", "opportunities": []}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {"error": "Invalid JSON", "opportunities": []}
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return {"error": str(e), "opportunities": []}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)
