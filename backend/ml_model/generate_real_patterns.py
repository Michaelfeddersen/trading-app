# backend/ml_model/generate_real_patterns.py

import yfinance as yf
import pandas as pd
import numpy as np
import os

# Liste der Aktien
STOCKS = ["AAPL", "TSLA", "WMT"]

# Download Settings
def download_data(ticker):
    data = yf.download(ticker, period="5y", interval="1d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    return data.dropna()

# Dummy-Pattern-Detector (Platzhalter!)
def detect_pattern(df):
    close = df['Close'].values
    if len(close) < 50:
        return None

    # Sehr einfache Heuristik: (nur zum Start)
    if close[-1] > close[-25] and np.min(close[-25:]) < close[-25] * 0.95:
        return "Double Bottom"
    if close[-1] < close[-25] and np.max(close[-25:]) > close[-25] * 1.05:
        return "Double Top"
    if close[-1] > close[-5] and np.std(close[-20:]) < 0.02 * np.mean(close[-20:]):
        return "Rising Wedge"
    if close[-1] < close[-5] and np.std(close[-20:]) < 0.02 * np.mean(close[-20:]):
        return "Falling Wedge"
    return "No Pattern"

# Daten erzeugen
def create_dataset():
    X = []
    y = []

    for ticker in STOCKS:
        df = download_data(ticker)

        for i in range(50, len(df)):
            window = df.iloc[i-50:i]
            pattern = detect_pattern(window)

            features = window[['Open', 'High', 'Low', 'Close']].values

            if pattern:
                X.append(features)
                y.append(pattern)

    return np.array(X), np.array(y)

if __name__ == "__main__":
    os.makedirs("ml_model/generated", exist_ok=True)

    X, y = create_dataset()
    np.save("ml_model/X_real.npy", X)
    np.save("ml_model/y_real.npy", y)

    print(f"✅ Datensatz erstellt: {X.shape[0]} Samples gespeichert!")
