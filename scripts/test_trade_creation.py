import requests
import json

# Test creating a trade without authentication
url = "http://localhost:8000/api/trades/"
headers = {"Content-Type": "application/json"}
data = {
    "symbol": "BTCUSDT",
    "side": "long",
    "entry_price": 45000.0,
    "quantity": 0.1,
    "notes": "Confident setup, good technical analysis"
}

print("Testing trade creation without authentication...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ SUCCESS! Trade created:")
        print(f"  Trade ID: {result['trade']['id']}")
        print(f"  Symbol: {result['trade']['symbol']}")
        print(f"  User: {result['trade']['user_id']}")
        print(f"  Side: {result['trade']['side']}")
        if result.get('nlp_analysis'):
            print(f"  Sentiment: {result['nlp_analysis'].get('sentiment_score', 'N/A')}")
            print(f"  Emotions: {len(result['nlp_analysis'].get('emotions', []))} detected")
        print("\nDemo mode is working! No authentication required.")
    else:
        print(f"\n✗ FAILED with status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Cannot connect to backend")
    print("Make sure backend is running on port 8000")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
