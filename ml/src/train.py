from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from keras.models import Sequential
from keras.layers import Dense, Conv1D, Flatten
import pandas as pd
import numpy as np
import joblib

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def preprocess_data(data):
    # Assuming the last column is the target variable
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    return X, y

def train_random_forest(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_cnn(X_train, y_train):
    model = Sequential()
    model.add(Conv1D(64, kernel_size=3, activation='relu', input_shape=(X_train.shape[1], 1)))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32)
    return model

def save_model(model, model_name):
    joblib.dump(model, f'ml/models/{model_name}.pkl')

def main():
    data = load_data('path/to/your/data.csv')
    X, y = preprocess_data(data)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_model = train_random_forest(X_train, y_train)
    save_model(rf_model, 'random_forest_model')

    # Reshape for CNN
    X_train_cnn = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    cnn_model = train_cnn(X_train_cnn, y_train)
    cnn_model.save('ml/models/cnn_model.h5')

if __name__ == "__main__":
    main()