import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class DataPreparation:
    def __init__(self, sequence_length=10):
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def load_data(self, file_path):
        df = pd.read_csv(file_path)
        return df

    def preprocess_data(self, df):
        scaled_data = self.scaler.fit_transform(df['Temperature'].values.reshape(-1, 1))
        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length - 10):
            X.append(scaled_data[i:i + self.sequence_length])
            y.append(scaled_data[i + self.sequence_length:i + self.sequence_length + 10])
        return np.array(X), np.array(y)

    def inverse_transform(self, data):
        return self.scaler.inverse_transform(data)