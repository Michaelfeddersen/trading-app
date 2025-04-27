# backend/ml_model/train_realistic_pattern_model.py

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Simuliere realistische Chartmuster
def generate_realistic_data(samples=1000):
    X = []
    y = []
    for _ in range(samples):
        pattern_type = np.random.randint(0, 4)
        
        if pattern_type == 0:  # Kein Muster
            base = np.cumsum(np.random.normal(0, 0.5, 50))
        elif pattern_type == 1:  # Double Bottom
            base = np.concatenate([
                np.linspace(1, 0, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(0, 1, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(1, 0.5, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(0.5, 1, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(1, 1.2, 10) + np.random.normal(0, 0.05, 10)
            ])
        elif pattern_type == 2:  # Double Top
            base = np.concatenate([
                np.linspace(0, 1, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(1, 0, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(0, 0.5, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(0.5, 0, 10) + np.random.normal(0, 0.05, 10),
                np.linspace(0, -0.2, 10) + np.random.normal(0, 0.05, 10)
            ])
        elif pattern_type == 3:  # Wedge
            base = np.linspace(0, 1, 50) + np.random.normal(0, 0.1, 50)
            base += np.linspace(0, -0.5, 50)
        
        # Simuliere Open/High/Low/Close aus einer Basislinie
        open_ = base + np.random.normal(0, 0.02, 50)
        high = open_ + np.random.uniform(0, 0.05, 50)
        low = open_ - np.random.uniform(0, 0.05, 50)
        close = open_ + np.random.normal(0, 0.02, 50)

        sequence = np.stack([open_, high, low, close], axis=1)
        X.append(sequence)
        y.append(pattern_type)

    return np.array(X), np.array(y)

# Generiere die Daten
X, y = generate_realistic_data(samples=5000)

# One-Hot-Encoding
y_cat = to_categorical(y, num_classes=4)

# Aufteilen in Training und Test
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Model definieren
model = Sequential()
model.add(LSTM(64, input_shape=(50, 4)))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dense(4, activation='softmax'))  # 4 Klassen

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Model trainieren
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=25, batch_size=32)

# Speichern
model.save('ml_model/pattern_multi_model_realistic.h5')

print("\n✅ Modell wurde erfolgreich gespeichert unter ml_model/pattern_multi_model_realistic.h5!")
