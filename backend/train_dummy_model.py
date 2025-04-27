import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import os

# Ordner erstellen, falls nicht vorhanden
os.makedirs('ml_model', exist_ok=True)

# Dummy-Modell erstellen
model = Sequential([
    LSTM(64, input_shape=(50, 4)),  # 50 Tage, 4 Werte (Open, High, Low, Close)
    Dense(1, activation='sigmoid')  # Eine Ausgabe: 0 oder 1
])

# Kompilieren
model.compile(optimizer='adam', loss='binary_crossentropy')

# Modell speichern
model.save('ml_model/pattern_model.h5')

print("✅ Dummy-Modell erfolgreich gespeichert unter ml_model/pattern_model.h5!")
