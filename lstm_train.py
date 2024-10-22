import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


Active_History = pd.read_csv('activehistory.csv')

def get_ratings_dict(df):
    ratings_dict = {}
    for _, row in df.iterrows():
        id_val = row['id']        
        ratings = row.drop(['id', 'name']).dropna().tolist()
        
        ratings_dict[id_val] = ratings
    return ratings_dict

Careers = get_ratings_dict(Active_History)
Careers = {key: np.diff(value) for key, value in Careers.items() if len(value) >= 50}

window_size = 5  # Use the last 5 ratings to predict the next

# Function to prepare sequences
def prepare_sequences(ratings, window_size):
    X, y = [], []
    for i in range(len(ratings) - window_size):
        X.append(ratings[i:i + window_size])
        y.append(ratings[i + window_size])
    return np.array(X), np.array(y)


X = np.ones([1,5])
y = np.ones([1,])
for driver in Careers:
    ratings = Careers[driver]
    print(driver)
    tempX, tempy = prepare_sequences(ratings, window_size)
    X = np.concatenate((X, tempX))
    y = np.concatenate((y, tempy))


X = np.delete(X, 1, 0)
y = np.delete(y, 1, 0)


# Reshape for LSTM (samples, timesteps, features)
X = X.reshape((X.shape[0], X.shape[1], 1))

# Build the LSTM model
model = Sequential([
    LSTM(100, activation='relu', return_sequences=True, input_shape=(window_size, 1)),
    LSTM(50, activation='tanh'),
    Dense(25, activation='relu'),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# Train the global model
model.fit(X, y, epochs=200, verbose=1)

model.save('nn_ratings_model.h5')