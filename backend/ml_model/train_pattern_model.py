import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import os

# Pfad zu den echten Musterdaten
DATA_PATH = 'real_patterns.csv'

# Laden der Daten
data = pd.read_csv(DATA_PATH)

# Feature Columns: Open, High, Low, Close
features = ['Open', 'High', 'Low', 'Close']

# Zielspalte (Pattern-Klassen)
pattern_mapping = {
    'Double Bottom': 0,
    'Double Top': 1,
    'Rising Wedge': 2,
    'Falling Wedge': 3
}

# Daten vorbereiten
X = []
y = []

SEQUENCE_LENGTH = 50

for i in range(len(data) - SEQUENCE_LENGTH):
    sequence = data[features].iloc[i:i+SEQUENCE_LENGTH].values
    label = data['pattern'].iloc[i+SEQUENCE_LENGTH-1]

    if label in pattern_mapping:
        X.append(sequence)
        y.append(pattern_mapping[label])

X = np.array(X)
y = np.array(y)

# Aufteilen in Training und Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Modell aufbauen
model = Sequential()
model.add(LSTM(64, input_shape=(SEQUENCE_LENGTH, 4), return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(32))
model.add(Dropout(0.3))
model.add(Dense(4, activation='softmax'))  # 4 Klassen

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Training
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=30, batch_size=32)

# Modell speichern
os.makedirs('ml_model', exist_ok=True)
model.save('ml_model/pattern_model_real.h5')

print("✅ Training abgeschlossen und Modell gespeichert!")
