from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

app = FastAPI()

# CORS erlauben (Frontend-Zugriff)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KI-Modell laden
try:
    model = load_model('ml_model/pattern_model.h5')
except Exception:
    print("Warnung: KI-Modell konnte nicht geladen werden.")
    model = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/detect/{ticker}")
async def detect_pattern(ticker: str):
    if model is None:
        raise HTTPException(status_code=501, detail="KI-Modell nicht verfügbar")
    
    data = yf.download(ticker, period="60d", interval="1d")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    if data.empty:
        raise HTTPException(status_code=400, detail="Keine Marktdaten verfügbar")

    required_columns = ['Open', 'High', 'Low', 'Close']
    if not set(required_columns).issubset(data.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Fehlende Spalten: {set(required_columns) - set(data.columns)}"
        )

    data = data.dropna(subset=required_columns)

    if len(data) < 50:
        raise HTTPException(
            status_code=400,
            detail=f"Nicht genügend Kursdaten ({len(data)} Tage, mind. 50 nötig)"
        )

    data_array = data[required_columns].values[-50:]

    try:
        prediction = model.predict(data_array.reshape(1, 50, 4))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Modellvorhersage: {str(e)}")

    confidence = float(prediction[0][0])

    return {
        "pattern": "Head and Shoulders" if confidence > 0.5 else "No pattern",
        "confidence": confidence,
        "entry_point": float(data['Close'].iloc[-1])
    }

@app.get("/stock/{ticker}")
async def get_stock(ticker: str, interval: str = "1d"):
    data = yf.download(ticker, period="60d", interval=interval)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if data.empty:
        raise HTTPException(status_code=404, detail="Keine Kursdaten gefunden")

    data = data.reset_index()

    keep_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    available_columns = [col for col in keep_columns if col in data.columns]
    data = data[available_columns]

    data["Date"] = data["Date"].astype(str)

    # SMA und RSI
    if 'Close' in data.columns:
        data['SMA_14'] = data['Close'].rolling(window=14).mean()

        delta = data['Close'].diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss
        data['RSI_14'] = 100 - (100 / (1 + rs))

        # EMA 14 und EMA 50 (neu!)
        data['EMA_14'] = data['Close'].ewm(span=14, adjust=False).mean()
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
    else:
        data['SMA_14'] = None
        data['RSI_14'] = None
        data['EMA_14'] = None
        data['EMA_50'] = None

    import numpy as np
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.fillna(value=np.nan)

    def safe_float(val):
        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            return None
        return float(val)

    def safe_int(val):
        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            return None
        return int(val)

    result = []
    for _, row in data.iterrows():
        result.append({
            "Date": row.get("Date"),
            "Open": safe_float(row.get("Open")),
            "High": safe_float(row.get("High")),
            "Low": safe_float(row.get("Low")),
            "Close": safe_float(row.get("Close")),
            "Volume": safe_int(row.get("Volume")),
            "SMA_14": safe_float(row.get("SMA_14")),
            "RSI_14": safe_float(row.get("RSI_14")),
            "EMA_14": safe_float(row.get("EMA_14")),
            "EMA_50": safe_float(row.get("EMA_50")),
        })

    return result




@app.get("/analyze/{ticker}")
async def analyze_stock(ticker: str):
    try:
        data = yf.download(ticker, period="60d", interval="1d", auto_adjust=False)
        if data.empty:
            raise HTTPException(status_code=404, detail="Keine Daten verfügbar")

        data = data.reset_index()

        last_close = float(data["Close"].iloc[-1])
        moving_avg = float(data["Close"].rolling(window=10).mean().iloc[-1])

        pattern = "Bullish (Preis > 10-Tage-Durchschnitt)" if last_close > moving_avg else "Bearish (Preis < 10-Tage-Durchschnitt)"

        return {
            "ticker": ticker,
            "pattern": pattern,
            "last_close": last_close,
            "moving_avg_10": moving_avg,
            "signal": "BUY" if last_close > moving_avg else "SELL"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")
