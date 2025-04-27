# backend/ml_model/pattern_detection.py

import numpy as np
from tensorflow.keras.models import load_model
import yfinance as yf
import pandas as pd

# Mehrere Modelle können hier später verwaltet werden
try:
    multi_model = load_model('ml_model/pattern_multi_model.h5')
except Exception:
    print("Warnung: Advanced Pattern Modell konnte nicht geladen werden.")
    multi_model = None

def load_stock_data(ticker, lookback_days=60):
    data = yf.download(ticker, period=f"{lookback_days}d", interval="1d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    if data.empty:
        raise ValueError("Keine Kursdaten verfügbar.")
    return data[['Open', 'High', 'Low', 'Close']]

def detect_advanced_patterns(ticker):
    if multi_model is None:
        raise Exception("Kein Modell geladen.")

    data = load_stock_data(ticker, lookback_days=60)
    data = data.dropna()

    if len(data) < 50:
        raise ValueError("Nicht genügend Kursdaten.")

    last_data = data.values[-50:]
    prediction = multi_model.predict(last_data.reshape(1, 50, 4))

    class_idx = np.argmax(prediction[0])
    confidence = float(np.max(prediction[0]))

    patterns = ["Kein Muster", "Double Bottom", "Wedge", "Head and Shoulders"]

    return {
        "pattern": patterns[class_idx],
        "confidence": confidence,
        "entry_point": float(data['Close'].iloc[-1])
    }
