#!/usr/bin/env python3
"""
Simple test script for the dashboard
"""
import asyncio
import httpx
import json

async def test_analytics_api():
    """Test the analytics API directly"""
    print("Testing analytics API...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://78.47.150.122:8080/api/analysis")
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            if 'opportunities' in data:
                print(f"Opportunities count: {len(data['opportunities'])}")
                if data['opportunities']:
                    first = data['opportunities'][0]
                    print(f"First opportunity: {first.get('symbol')} - {first.get('composite_score')} - {first.get('entry_recommendation')}")
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

async def test_bot_health():
    """Test the bot health API"""
    print("\nTesting bot health API...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://78.47.150.122:8000/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    print("=== DASHBOARD API TESTS ===")
    
    # Test analytics
    analytics_data = await test_analytics_api()
    
    # Test bot health  
    bot_healthy = await test_bot_health()
    
    print(f"\n=== RESULTS ===")
    print(f"Analytics API: {'✓' if analytics_data else '✗'}")
    print(f"Bot Health: {'✓' if bot_healthy else '✗'}")
    
    if analytics_data and 'opportunities' in analytics_data:
        print(f"Live opportunities: {len(analytics_data['opportunities'])}")

if __name__ == "__main__":
    asyncio.run(main())
