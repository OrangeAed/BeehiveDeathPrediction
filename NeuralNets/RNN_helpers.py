import os
from typing import List
from keras import callbacks
import numpy as np
from datetime import datetime

from TemperatureAnalysis.collect_data import CollectData

def collect_data(hivename: str, start_date: datetime, end_date: datetime):
    cd = CollectData()
    df = cd.get_temp_dataframe(hivename, start_date, end_date)
    df = cd.get_temp_dataframe_averaged_by_day(df=df, is_temp=True)

    # Encode day of year in a circle
    def encode_day_of_year(date: datetime):
        day_of_year = date.timetuple().tm_yday
        angle = 2 * np.pi * (day_of_year / 365.0)
        sin_value = np.sin(angle)
        cos_value = np.cos(angle)
        return sin_value, cos_value

    df['sin_day_of_year'], df['cos_day_of_year'] = zip(*df['Time'].apply(encode_day_of_year))

    return df

def save_data(df, hivename: str, problem, year: str, features: List[str] = None, timesteps=30, overwrite=False):
    if features is None:
        features = df.columns.tolist()

    data = df[features].values
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

    # Save the data
    file_dir = f"data/{problem}"
    os.makedirs(file_dir, exist_ok=True)
    filename = f"{hivename}_{year}.npz"
    if os.path.exists(f"{file_dir}/{filename}"):
        if not overwrite:
            print(f"File {filename} already exists. Set overwrite=True to overwrite it.")
            return
        else:
            os.remove(f"{file_dir}/{filename}")
    np.savez(f"{file_dir}/{filename}", X=X, y=y)


def getXY(problem, hivename, year):
    npz_file = f"data/{problem}/{hivename}_{year}.npz"
    with np.load(npz_file, allow_pickle=True) as data:
        X = data['X'].astype(np.float32)
        y = data['y'].astype(np.float32)
    return X, y



def summarize_models():
    for model_path in os.listdir('models'):
        print(f"Model: {model_path}")

