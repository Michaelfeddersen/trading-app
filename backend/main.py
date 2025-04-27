from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import datetime
from ml_model.pattern_detection import detect_advanced_patterns

app = FastAPI()

# CORS erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KI Modell
try:
    model_basic = load_model('ml_model/pattern_model.h5')                   # 1. einfaches Modell (nur Head&Shoulders)
    model_multi = load_model('ml_model/pattern_multi_model.h5')              # 2. KI für mehrere einfache Muster
    model_multi_realistic = load_model('ml_model/pattern_multi_model_realistic.h5')  # 3. realistische multiple Muster
    model_real = load_model('ml_model/pattern_real_model.h5')                # 4. echtes realistisches Modell
except Exception:
    print("Warnung: Modelle konnten nicht geladen werden.")
    model_basic = None
    model_multi = None
    model_multi_realistic = None
    model_real = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/detect/{ticker}")
async def detect_pattern(ticker: str):
    if model_basic is None:
        raise HTTPException(status_code=501, detail="KI-Modell nicht verfügbar")
    
    data = yf.download(ticker, period="10y", interval="1wk")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    if data.empty:
        raise HTTPException(status_code=400, detail="Keine Marktdaten verfügbar")

    required_columns = ['Open', 'High', 'Low', 'Close']
    if not set(required_columns).issubset(data.columns):
        raise HTTPException(status_code=400, detail=f"Fehlende Spalten: {set(required_columns) - set(data.columns)}")

    data = data.dropna(subset=required_columns)

    if len(data) < 50:
        raise HTTPException(status_code=400, detail=f"Nicht genügend Kursdaten ({len(data)} Tage, mind. 50 nötig)")

    data_array = data[required_columns].values[-50:]

    try:
        prediction = model_basic.predict(data_array.reshape(1, 50, 4))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei Modellvorhersage: {str(e)}")

    confidence = float(prediction[0][0])

    return {
        "pattern": "Head and Shoulders" if confidence > 0.5 else "No pattern",
        "confidence": confidence,
        "entry_point": float(data['Close'].iloc[-1])
    }

@app.get("/stock/{ticker}")
async def get_stock(ticker: str, interval: str = Query(default="1d")):
    try:
        print(f"Abruf: {ticker} mit Interval: {interval}")

        # Dynamische Einstellungen
        if interval == "1d":
            yf_period = "5d"
            yf_interval = "5m"
        elif interval == "5d":
            yf_period = "5d"
            yf_interval = "15m"
        elif interval == "1mo":
            yf_period = "1mo"
            yf_interval = "30m"
        elif interval == "3mo":
            yf_period = "3mo"
            yf_interval = "60m"
        elif interval == "6mo":
            yf_period = "6mo"
            yf_interval = "1d"
        elif interval == "1y":
            yf_period = "1y"
            yf_interval = "1d"
        elif interval == "5y":
            yf_period = "5y"
            yf_interval = "1wk"
        elif interval == "10y":
            yf_period = "10y"
            yf_interval = "1wk"  # Wochenkerzen
        elif interval == "ytd":
            yf_period = "ytd"
            yf_interval = "1d"
        elif interval == "max":
            yf_period = "max"
            yf_interval = "1wk"
        else:
            raise HTTPException(status_code=400, detail="Ungültiges Intervall")

        if interval == "10y":
            end_date = datetime.datetime.today()
            start_date = end_date - datetime.timedelta(days=365*10)
            yf_data = yf.download(ticker, start=start_date, end=end_date, interval="1mo", auto_adjust=True)
        else:
            yf_data = yf.download(ticker, period=yf_period, interval=yf_interval, auto_adjust=True)

        if isinstance(yf_data.columns, pd.MultiIndex):
            yf_data.columns = yf_data.columns.droplevel(1)

        if yf_data.empty:
            raise HTTPException(status_code=404, detail="Keine Kursdaten gefunden")

        yf_data = yf_data.reset_index()

        # Technische Indikatoren
        yf_data['SMA_14'] = yf_data['Close'].rolling(window=14).mean()
        yf_data['EMA_14'] = yf_data['Close'].ewm(span=14, adjust=False).mean()
        yf_data['EMA_50'] = yf_data['Close'].ewm(span=50, adjust=False).mean()

        delta = yf_data['Close'].diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss
        yf_data['RSI_14'] = 100 - (100 / (1 + rs))

        yf_data['Bollinger_Mid'] = yf_data['Close'].rolling(window=20).mean()
        boll_std = yf_data['Close'].rolling(window=20).std()
        yf_data['Bollinger_Upper'] = yf_data['Bollinger_Mid'] + (boll_std * 2)
        yf_data['Bollinger_Lower'] = yf_data['Bollinger_Mid'] - (boll_std * 2)


        exp1 = yf_data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = yf_data['Close'].ewm(span=26, adjust=False).mean()
        yf_data['MACD'] = exp1 - exp2
        yf_data['MACD_Signal'] = yf_data['MACD'].ewm(span=9, adjust=False).mean()

        yf_data = yf_data.replace([np.inf, -np.inf], np.nan)
        yf_data = yf_data.fillna(value=np.nan)

        # Jetzt korrekt
        filtered = yf_data

        result = []
        for _, row in filtered.iterrows():
            result.append({
                "Date": str(row["Datetime"]) if "Datetime" in row else str(row["Date"]),
                "Open": float(row["Open"]) if not pd.isna(row["Open"]) else None,
                "High": float(row["High"]) if not pd.isna(row["High"]) else None,
                "Low": float(row["Low"]) if not pd.isna(row["Low"]) else None,
                "Close": float(row["Close"]) if not pd.isna(row["Close"]) else None,
                "Volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                "SMA_14": float(row["SMA_14"]) if not pd.isna(row["SMA_14"]) else None,
                "EMA_14": float(row["EMA_14"]) if not pd.isna(row["EMA_14"]) else None,
                "EMA_50": float(row["EMA_50"]) if not pd.isna(row["EMA_50"]) else None,
                "RSI_14": float(row["RSI_14"]) if not pd.isna(row["RSI_14"]) else None,
                "Bollinger_Mid": float(row["Bollinger_Mid"]) if not pd.isna(row["Bollinger_Mid"]) else None,
                "Bollinger_Upper": float(row["Bollinger_Upper"]) if not pd.isna(row["Bollinger_Upper"]) else None,
                "Bollinger_Lower": float(row["Bollinger_Lower"]) if not pd.isna(row["Bollinger_Lower"]) else None,
                "MACD": float(row["MACD"]) if not pd.isna(row["MACD"]) else None,
                "MACD_Signal": float(row["MACD_Signal"]) if not pd.isna(row["MACD_Signal"]) else None,
            })

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Serverfehler: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Serverfehler: {str(e)}")
# Einfaches KI Modell
# Einfaches Basic Modell
@app.get("/detect_real/{ticker}")
async def detect_real(ticker: str):
    try:
        if model_real is None:
            raise HTTPException(status_code=501, detail="Echtes Modell nicht verfügbar")

        data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        if data.empty or len(data) < 50:
            raise HTTPException(status_code=400, detail="Keine gültigen Daten")

        required_columns = ['Open', 'High', 'Low', 'Close']
        data = data.dropna(subset=required_columns)

        X = data[required_columns].values[-50:].reshape(1, 50, 4)
        prediction = model_real.predict(X)
        prediction_class = np.argmax(prediction)

        classes = {0: "Kein Muster", 1: "Double Bottom", 2: "Wedge", 3: "Head and Shoulders"}

        # Start und Enddatum (z.B. die letzten 50 Tage)
        start_date = data.index[-50].strftime('%Y-%m-%d')
        end_date = data.index[-1].strftime('%Y-%m-%d')

        return {
            "pattern": classes.get(prediction_class, "Unbekannt"),
            "confidence": float(np.max(prediction)),
            "entry_point": float(data['Close'].iloc[-1]),
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Multimuster Dummy Modell
@app.get("/detect_multi/{ticker}")
async def detect_multi(ticker: str):
    try:
        if model_multi is None:
            raise HTTPException(status_code=501, detail="Multi-Modell nicht verfügbar")

        data = yf.download(ticker, period="3mo", interval="1d", auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        if data.empty or len(data) < 50:
            raise HTTPException(status_code=400, detail="Keine gültigen Daten")

        required_columns = ['Open', 'High', 'Low', 'Close']
        data = data.dropna(subset=required_columns)

        X = data[required_columns].values[-50:].reshape(1, 50, 4)
        prediction = model_multi.predict(X)
        prediction_class = np.argmax(prediction)

        classes = {0: "Kein Muster", 1: "Double Bottom", 2: "Wedge", 3: "Head and Shoulders"}

        return {
            "pattern": classes.get(prediction_class, "Unbekannt"),
            "confidence": float(np.max(prediction)),
            "entry_point": float(data['Close'].iloc[-1])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Realistische Multi-Muster
@app.get("/detect_multi_real/{ticker}")
async def detect_multi_real(ticker: str):
    try:
        if model_multi_realistic is None:
            raise HTTPException(status_code=501, detail="Realistisches Multi-Modell nicht verfügbar")

        data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        if data.empty or len(data) < 50:
            raise HTTPException(status_code=400, detail="Keine gültigen Daten")

        required_columns = ['Open', 'High', 'Low', 'Close']
        data = data.dropna(subset=required_columns)

        X = data[required_columns].values[-50:].reshape(1, 50, 4)
        prediction = model_multi_realistic.predict(X)
        prediction_class = np.argmax(prediction)

        classes = {0: "Kein Muster", 1: "Double Bottom", 2: "Wedge", 3: "Head and Shoulders"}

        return {
            "pattern": classes.get(prediction_class, "Unbekannt"),
            "confidence": float(np.max(prediction)),
            "entry_point": float(data['Close'].iloc[-1])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Echtes realistisches Modell
@app.get("/detect_real/{ticker}")
async def detect_real(ticker: str):
    try:
        if model_real is None:
            raise HTTPException(status_code=501, detail="Echtes Modell nicht verfügbar")

        data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        if data.empty or len(data) < 50:
            raise HTTPException(status_code=400, detail="Keine gültigen Daten")

        required_columns = ['Open', 'High', 'Low', 'Close']
        data = data.dropna(subset=required_columns)

        X = data[required_columns].values[-50:].reshape(1, 50, 4)
        prediction = model_real.predict(X)
        prediction_class = np.argmax(prediction)

        classes = {0: "Kein Muster", 1: "Double Bottom", 2: "Wedge", 3: "Head and Shoulders"}

        return {
            "pattern": classes.get(prediction_class, "Unbekannt"),
            "confidence": float(np.max(prediction)),
            "entry_point": float(data['Close'].iloc[-1])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fortgeschrittene Regeln
@app.get("/detect_advanced/{ticker}")
async def detect_advanced(ticker: str):
    try:
        result = detect_advanced_patterns(ticker)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
