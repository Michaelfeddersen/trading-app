import numpy as np
import pandas as pd
import yfinance as yf
from tensorflow.keras import layers, models

# 1. Echte Daten herunterladen (Beispiel: S&P 500 Aktien)
def download_data(ticker, days=50):
    data = yf.download(ticker, period=f"{days}d", interval="1d")
    return data[['Open', 'High', 'Low', 'Close']].values

# 2. Synthetische Labels generieren (Beispiel: Nur für Demo!)
# In der Praxis würdest du hier manuell gelabelte Daten verwenden (z. B. von Kaggle).
X_train = np.array([download_data("AAPL") for _ in range(100)])  # 100 Fake-Samples
y_train = np.random.randint(0, 2, 100)  # Zufällige Labels (0/1)

# 3. CNN-Modell (wie zuvor)
model = models.Sequential([
    layers.Reshape((50, 4, 1), input_shape=(50, 4)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10)

# 4. Modell speichern
model.save('ml_model/pattern_model.h5')