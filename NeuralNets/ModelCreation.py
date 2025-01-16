from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

class ModelCreation:
    def __init__(self, sequence_length):
        self.sequence_length = sequence_length

    def create_model(self):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(self.sequence_length, 1)))
        model.add(LSTM(units=50))
        model.add(Dense(units=10))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model