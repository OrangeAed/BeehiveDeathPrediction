class ModelTraining:
    def __init__(self, model):
        self.model = model

    def train_model(self, X_train, y_train, epochs=20, batch_size=32):
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)