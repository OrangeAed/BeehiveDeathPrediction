class Prediction:
    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def make_predictions(self, X_test):
        predictions = self.model.predict(X_test)
        return self.scaler.inverse_transform(predictions)

    def predict_next_10_days(self, last_sequence):
        last_sequence = last_sequence.reshape((1, len(last_sequence), 1))
        next_10_days_prediction = self.model.predict(last_sequence)
        return self.scaler.inverse_transform(next_10_days_prediction)