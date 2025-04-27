from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from tensorflow.keras.models import load_model  # Diesen Import hinzufügen

app = FastAPI()

# CORS erlauben (für Frontend-Zugriff)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# KI-Modell laden (nur wenn die Datei existiert)
try:
    model = load_model('ml_model/pattern_model.h5')
except:
    print("Warnung: KI-Modell konnte nicht geladen werden. Stelle sicher, dass die Datei existiert.")
    model = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/detect/{ticker}")
async def detect_pattern(ticker: str):
    if model is None:
        raise HTTPException(status_code=501, detail="KI-Modell nicht verfügbar")
    
# 1. Daten holen
    data = yf.download(ticker, period="60d", interval="1d")

# Wenn MultiIndex → Ebene 1 droppen
    if isinstance(data.columns, pd.MultiIndex):
     data.columns = data.columns.droplevel(1)

# Prüfen ob Daten geladen wurden
    if data.empty:
     raise HTTPException(status_code=400, detail="Keine Marktdaten verfügbar")

    required_columns = ['Open', 'High', 'Low', 'Close']

# Prüfen ob wirklich alle Spalten vorhanden sind
    if not set(required_columns).issubset(set(data.columns)):
        raise HTTPException(
        status_code=400,
        detail=f"Fehlende Spalten in Marktdaten: {set(required_columns) - set(data.columns)}"
    )

# Jetzt sicher: Spalten vorhanden → NaN entfernen
    data = data.dropna(subset=required_columns)

    if data.shape[0] < 50:
        raise HTTPException(
            status_code=400,
         detail=f"Nicht genügend Kursdaten vorhanden ({data.shape[0]} Tage, mind. 50 nötig)"
    )

# 2. Daten vorbereiten
    data_array = data[required_columns].values[-50:]

# 3. Vorhersage machen
    try:
         prediction = model.predict(data_array.reshape(1, 50, 4))
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Fehler bei Modellvorhersage: {str(e)}")

    confidence = float(prediction[0][0])

# 4. Ergebnis zurückgeben
    return {
     "pattern": "Head and Shoulders" if confidence > 0.5 else "No pattern",
     "confidence": confidence,
     "entry_point": float(data['Close'].iloc[-1])
}




@app.get("/stock/{ticker}")
async def get_stock(ticker: str, interval: str = "1d"):
    data = yf.download(ticker, period="60d", interval=interval)
    return data.reset_index().to_dict(orient="records")

@app.get("/analyze/{ticker}")
async def analyze_stock(ticker: str):
    try:
        # 1. Aktiendaten holen
        data = yf.download(ticker, period="60d", interval="1d", auto_adjust=False)
        if data.empty:
            raise HTTPException(status_code=404, detail="Keine Daten verfügbar")

        data = data.reset_index()
        print("Daten erhalten:", data.columns)  # Debug

        # 2. Werte explizit als Float extrahieren
        last_close = float(data["Close"].iloc[-1])
        moving_avg = float(data["Close"].rolling(window=10).mean().iloc[-1])

        # 3. Signal bestimmen
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
    

    