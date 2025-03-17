import os

import tensorflow as tf
import numpy as np
from keras import layers, models, utils, optimizers, callbacks, Sequential
from keras.src.optimizers import Adam
from datetime import datetime

from TemperatureAnalysis.collect_data import CollectData

class RecurrentNeuralNet:
    def __init__(self, problem="temperature", hivename='AppMAIS1L',
                 start_date=datetime(2022, 4, 10),
                 end_date=datetime(2023, 4, 22),):
        # self.input_size = input_size
        self.output_size = 1
        self.problem = problem
        self.hivename = hivename
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.collect_data()


    def create_model(self, X, hidden_size, num_layers, activation='tanh', output_activation='linear') -> Sequential:
        model = Sequential()
        model.add(layers.Input(shape=(None, 3)))  #
        for i in range(num_layers):
            model.add(layers.SimpleRNN(hidden_size, activation=activation,
                                            return_sequences=True if i < num_layers - 1 else False,
                                            ))
        model.add(layers.Dense(self.output_size, activation=output_activation))
        return model

    def collect_data(self):
        def encode_day_of_year(date: datetime):
            day_of_year = date.timetuple().tm_yday
            angle = 2 * np.pi * (day_of_year / 365.0)
            sin_value = np.sin(angle)
            cos_value = np.cos(angle)
            return sin_value, cos_value

        cd = CollectData()
        df = cd.get_temp_dataframe(self.hivename, self.start_date, self.end_date)
        df = cd.get_temp_dataframe_averaged_by_day(df=df, is_temp=True)

        # Encode day of year in a circle
        df['sin_day_of_year'], df['cos_day_of_year'] = zip(*df['Time'].apply(encode_day_of_year))

        return df

    def save_data(self, timesteps=30):
        features = ['InternalTemperature', 'ExternalTemperature', 'TemperatureDifference',
                    'ProportionalTemperatureDifference', 'sin_day_of_year', 'cos_day_of_year']
        data = self.data[features].values
        X, y = [], []

        # Calculate the number of sequences
        num_sequences = len(data) // timesteps

        for i in range(num_sequences):
            start_idx = i * timesteps
            end_idx = start_idx + timesteps
            X.append(data[start_idx:end_idx])
            y.append(data[end_idx - 1, 0])

        X = np.array(X)
        y = np.array(y)

        file_dir = f"data/{self.problem}"
        os.makedirs(file_dir, exist_ok=True)
        filename = f"{self.hivename}_{self.start_date.strftime('%Y')}.npz"
        np.savez(f"{file_dir}/{filename}", X=X, y=y)


    def train(self, X, y, model, epochs=10):
        model.compile(loss='mse', optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])
        model.fit(X, y, epochs=epochs)

    def predict(self, X, model):
        return np.argmax(model.predict(X), axis=-1)


if __name__ == '__main__':
    # input_size = 1 + 2 # current temp, time of year encoded in a circle
    rnn = RecurrentNeuralNet()
    rnn.save_data()
