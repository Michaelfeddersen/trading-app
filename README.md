# Trading App 📈

Dies ist eine Fullstack Trading-Applikation bestehend aus:

- **Backend**: FastAPI-Server mit Aktienanalyse und Mustererkennung (KI-Modell)
- **Frontend**: React-Frontend zum Visualisieren von Aktienkursen und Erkennen von Mustern

## Projektstruktur

- `/backend/` → FastAPI Server, TensorFlow Modell
- `/frontend/` → React Web App, Chart-Visualisierung (z.B. mit Lightweight Charts)

## Starten des Projekts

### Backend
```bash
cd backend
uvicorn main:app --reload
