import tensorflow as tf

def main():
    print("TensorFlow Version:", tf.__version__)
    
    # Mini-Daten
    inputs = tf.constant([[1.0, 2.0, 3.0]])
    
    # Kleine Dense-Schicht (Fully Connected Layer)
    dense = tf.keras.layers.Dense(units=1)
    
    # Forward Pass
    output = dense(inputs)
    
    print("Vorhersage:", output.numpy())

if __name__ == "__main__":
    main()
