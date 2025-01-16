from sklearn.model_selection import train_test_split

from NeuralNets.DataPreparation import  DataPreparation
from NeuralNets.ModelCreation import ModelCreation
from NeuralNets.ModelTraining import ModelTraining
from NeuralNets.Prediction import Prediction

# Initialize classes
data_prep = DataPreparation(sequence_length=10)
model_creator = ModelCreation(sequence_length=10)
model = model_creator.create_model()
trainer = ModelTraining(model)
predictor = Prediction(model, data_prep.scaler)

# Load and preprocess data
df = data_prep.load_data('temperature_data.csv')
X, y = data_prep.preprocess_data(df)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
trainer.train_model(X_train, y_train)

# Make predictions
predictions = predictor.make_predictions(X_test)
print("Predictions:", predictions)

# Predict next 10 days
last_sequence = X[-1]
next_10_days_prediction = predictor.predict_next_10_days(last_sequence)
print("Next 10 days temperature prediction:", next_10_days_prediction)