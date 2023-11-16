from tensorflow.keras.models import load_model

# Path to your model file
model_path = './models/model.h5'

# Load the model
model = load_model(model_path)

# Print the model summary
model.summary()
