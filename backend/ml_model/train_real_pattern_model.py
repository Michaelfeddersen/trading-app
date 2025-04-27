import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder   # <-- HINZUFÜGEN

# 📦 Echte Daten laden
X = np.load('ml_model/X_real.npy')
y = np.load('ml_model/y_real.npy')

# 🔥 Labels als Integer encodieren
label_encoder = LabelEncoder()
y_int = label_encoder.fit_transform(y)

# 📚 Labels One-Hot encodieren
y_cat = to_categorical(y_int, num_classes=len(label_encoder.classes_))

# 🧪 Splitten in Training/Test
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# 🏗️ Modell definieren
model = Sequential()
model.add(LSTM(64, input_shape=(50, 4)))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dense(len(label_encoder.classes_), activation='softmax'))  # <--- Korrekt für viele Klassen

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 🚀 Training starten
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=30, batch_size=32)

# 💾 Modell speichern
model.save('ml_model/pattern_real_model.h5')

# 💾 Label Encoder speichern für später (Optional)
import pickle
with open('ml_model/label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)

print("✅ Echt trainiertes Modell gespeichert unter: ml_model/pattern_real_model.h5")
