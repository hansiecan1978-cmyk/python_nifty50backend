from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from datetime import datetime

app = FastAPI()

NIFTY50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "BAJFINANCE.NS", "LICI.NS", "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS",
    "HDFC.NS", "AXISBANK.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS"
]

def calculate_probability(data):
    # Calculate 30-min momentum
    momentum = (data['Close'][-1] - data['Close'][-6]) / data['Close'][-6] * 100
    
    # Calculate volume spike
    volume_avg = data['Volume'][-10:-1].mean()
    volume_spike = data['Volume'][-1] / volume_avg if volume_avg > 0 else 1
    
    # Simple scoring algorithm
    score = 0
    if abs(momentum) > 0.5: score += 30
    if volume_spike > 1.8: score += 40
    if data['Close'][-1] > data['Close'].mean(): score += 30
    
    return min(100, score)

@app.get("/scan")
def scan_stocks():
    results = []
    for symbol in NIFTY50:
        try:
            data = yf.download(symbol, period="1d", interval="5m", progress=False)
            if len(data) < 10: continue
                
            probability = calculate_probability(data)
            last_close = data['Close'][-1]
            prev_close = data['Close'][-2]
            change = (last_close - prev_close) / prev_close * 100
            
            results.append({
                "symbol": symbol.replace(".NS", ""),
                "price": round(last_close, 2),
                "change": round(change, 2),
                "probability": round(probability),
                "direction": "buy" if change > 0 else "sell"
            })
        except:
            continue
    
    # Sort by highest probability
    return sorted(results, key=lambda x: x['probability'], reverse=True)[:10]