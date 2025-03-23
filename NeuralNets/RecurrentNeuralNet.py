import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import KFold
from keras import layers, callbacks, Sequential
from keras.src.optimizers import Adam
from datetime import datetime
import logging

from TemperatureAnalysis.collect_data import CollectData
from RNN_helpers import collect_data, save_data, getXY

def setup_logging(log_file='rnn_training.log'):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
class RecurrentNeuralNet:
    def __init__(self, problem="temperature", hivename='AppMAIS1L',
                 start_date=datetime(2022, 4, 10),
                 end_date=datetime(2023, 4, 22), ):
        # self.input_size = input_size
        self.output_size = 1
        self.problem = problem
        self.hivename = hivename
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.collect_data()

    def create_model(self, X, hidden_size, num_layers, activation='tanh', output_activation='linear') -> Sequential:
        model = Sequential()
        model.add(layers.Input(shape=(None, X.shape[-1])))

        norm_layer = layers.Normalization()
        norm_layer.adapt(X)
        model.add(norm_layer)

        for i in range(num_layers):
            model.add(layers.SimpleRNN(hidden_size, activation=activation,
                                       return_sequences=True if i < num_layers - 1 else False,
                                       ))

        model.add(layers.Dense(self.output_size, activation=output_activation))
        return model

    def collect_data(self):
        return collect_data(self.hivename, self.start_date, self.end_date)

    def save_data(self, timesteps=30):
        features = ['InternalTemperature', 'ExternalTemperature', 'TemperatureDifference',
                    'ProportionalTemperatureDifference', 'sin_day_of_year', 'cos_day_of_year']

        save_data(self.data, self.hivename, self.problem, self.start_date.strftime('%Y'), features, timesteps)

    def get_callbacks(self, checkpoint=True, early_stop=True, reduce_lr=True):
        callbacks_list = []
        if checkpoint:
            model_path = f'models/{self.problem}/{self.hivename}/{datetime.now().strftime("%Y%m%d%H%M%S")}.keras'
            model_checkpoint = callbacks.ModelCheckpoint(
                model_path,
                save_weights_only=False,
                save_freq='epoch',
                save_best_only=True,
                monitor='val_loss',
                verbose=1
            )
            callbacks_list.append(model_checkpoint)

        if early_stop:
            early_stopping = callbacks.EarlyStopping(
                monitor='val_loss',
                patience=200,
                verbose=1,
                min_delta=0.001,
                restore_best_weights=True
            )
            callbacks_list.append(early_stopping)

        if reduce_lr:
            lr_scheduler = callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.1,
                patience=50,
                verbose=1,
                min_delta=0.001,
                min_lr=1e-10
            )
            callbacks_list.append(lr_scheduler)

        return callbacks_list

    def train(self, X, y, model, callbacks, epochs=500):
        model.compile(loss='mse', optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])
        model.fit(X, y, epochs=epochs, callbacks=callbacks)

    def train_and_evaluate(self, X, y, hidden_size, num_layers, epochs=1000, k=5):
        kf = KFold(n_splits=k, shuffle=True, random_state=42)
        fold_no = 1
        history_list = []
        for train_index, val_index in kf.split(X):
            X_train, X_val = X[train_index], X[val_index]
            y_train, y_val = y[train_index], y[val_index]

            model = self.create_model(X, hidden_size, num_layers)
            model.compile(loss='mse', optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])

            logging.info(f'Training fold {fold_no}...')
            history = model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val), callbacks=self.get_callbacks())
            history_list.append(history.history)
            fold_no += 1

        self.plot_results(history_list)

    def plot_results(self, history_list):
        plt.figure(figsize=(12, 6))

        # Plot training & validation loss values
        plt.subplot(1, 2, 1)
        for i, history in enumerate(history_list):
            # plt.plot(history['loss'], label=f'Train Fold {i + 1}')
            plt.plot(history['val_loss'], label=f'Val Fold {i + 1}')
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(loc='upper right')

        # Plot training & validation accuracy values
        plt.subplot(1, 2, 2)
        for i, history in enumerate(history_list):
            # plt.plot(history['accuracy'], label=f'Train Fold {i + 1}')
            plt.plot(history['val_accuracy'], label=f'Val Fold {i + 1}')
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(loc='upper left')

        plt.tight_layout()
        plt.show()

    def predict(self, X, model):
        return np.argmax(model.predict(X), axis=-1)


if __name__ == '__main__':
    # input_size = 1 + 2 # current temp, time of year encoded in a circle
    setup_logging()
    rnn = RecurrentNeuralNet()
    rnn.save_data()
    X, y = getXY(rnn.problem, rnn.hivename, rnn.start_date.strftime('%Y'))
    # model = rnn.create_model(X, hidden_size=64, num_layers=2)
    # rnn.train(X, y, model, callbacks)
    # print(rnn.predict(X, model))

    rnn.train_and_evaluate(X, y, hidden_size=64, num_layers=2)



