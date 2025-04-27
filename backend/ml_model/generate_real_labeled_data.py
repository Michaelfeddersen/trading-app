# backend/ml_model/generate_real_labeled_data.py

import numpy as np
import yfinance as yf
import os

# Muster-Erkennung (ganz einfache Logik)
def detect_double_bottom(prices):
    if len(prices) < 30:
        return False
    min1 = np.argmin(prices[:len(prices)//2])
    min2 = np.argmin(prices[len(prices)//2:]) + len(prices)//2
    diff = abs(prices[min1] - prices[min2])
    return diff / np.mean([prices[min1], prices[min2]]) < 0.05

def detect_wedge(prices):
    if len(prices) < 30:
        return False
    trend = np.polyfit(np.arange(len(prices)), prices, 1)[0]
    return abs(trend) < 0.02

def detect_head_shoulders(prices):
    if len(prices) < 30:
        return False
    mid = len(prices) // 2
    left = np.max(prices[:mid//2])
    head = np.max(prices[mid//2:mid + mid//2])
    right = np.max(prices[mid + mid//2:])
    return head > left and head > right and abs(left - right) / head < 0.1

# Aktienliste
TICKERS = ["AAPL", "TSLA", "WMT"]

def generate_real_labeled_data(save_dir="backend/ml_model/real_data"):
    os.makedirs(save_dir, exist_ok=True)

    X = []
    y = []

    for ticker in TICKERS:
        print(f"Lade {ticker}...")
        data = yf.download(ticker, period="10y", interval="1wk", auto_adjust=True)
        closes = data['Close'].values

        # Sliding Window
        window_size = 50
        for i in range(len(closes) - window_size):
            window = closes[i:i+window_size]

            label = 0  # Kein Muster
            if detect_double_bottom(window):
                label = 1
            elif detect_wedge(window):
                label = 2
            elif detect_head_shoulders(window):
                label = 3

            X.append(window)
            y.append(label)

    X = np.array(X)
    y = np.array(y)

    np.save(os.path.join(save_dir, "X.npy"), X)
    np.save(os.path.join(save_dir, "y.npy"), y)

    print(f"✅ Fertig! {len(X)} Samples gespeichert unter {save_dir}")

if __name__ == "__main__":
    generate_real_labeled_data()
