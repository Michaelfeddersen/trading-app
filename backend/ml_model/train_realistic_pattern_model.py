import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# 🎯 Realistische Dummy-Daten erzeugen
def generate_realistic_data(samples=2000):
    X = []
    y = []

    for _ in range(samples):
        # Basisdaten
        base = np.cumsum(np.random.randn(50)) + 100  # Kurslinie mit leichtem Rauschen

        # Entscheide zufällig, ob wir ein Muster einbauen
        label = np.random.choice([0, 1, 2, 3])

        if label == 1:  # Double Bottom simulieren
            pos = np.random.randint(10, 30)
            base[pos] -= 10
            base[pos+5] -= 10
        elif label == 2:  # Wedge simulieren
            base = np.linspace(100, 110, 50) + np.random.randn(50)
        elif label == 3:  # Head and Shoulders simulieren
            pos = np.random.randint(10, 30)
            base[pos] += 15
            base[pos+5] -= 10
            base[pos+10] += 15

        X.append(np.column_stack([
            base + np.random.randn(50) * 0.5,  # Open
            base + np.random.randn(50) * 0.5,  # High
            base + np.random.randn(50) * 0.5,  # Low
            base + np.random.randn(50) * 0.5,  # Close
        ]))
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    return X, y

# 📊 Daten erstellen
X, y = generate_realistic_data(3000)

# 📚 Label one-hot encodieren
y_cat = to_categorical(y, num_classes=4)

# 🧪 Daten splitten
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# 🏗️ Modell bauen
model = Sequential()
model.add(LSTM(64, input_shape=(50, 4)))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dense(4, activation='softmax'))  # 4 Klassen

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 🚀 Training
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=20, batch_size=32)

# 💾 Speichern
model.save('ml_model/pattern_multi_model.h5')

print("✅ Das neue realistische Modell wurde gespeichert unter ml_model/pattern_multi_model.h5")
