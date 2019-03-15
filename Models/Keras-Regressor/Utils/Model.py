import keras
from keras.models import model_from_json
from keras import Sequential, initializers
import keras.backend as K
from keras.layers import Dense, Dropout
from Utils.Metrics import rmse
from Utils.Configuration import Config
from Utils.Utilities import model_path
import json
import os


# Model definition for a simple linear regressor
def LinearRegressor(input_dim):
    model = Sequential()
    model.add(Dense(1, input_dim=input_dim, kernel_initializer='normal', activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mse', 'mape', rmse])
    return model


def DNNRegressor(input_dim, output_dim, config):
    # Some sources say that with ReLU activations, the biases should not be zero initialized.
    # This is because it can result in "dead neurons".

    model = Sequential()

    # Adds input layer and first hidden layer
    model.add(Dense(config['cells_per_layer'], input_dim=input_dim, kernel_initializer=config['kernel_initializer'], bias_initializer=initializers.Constant(0.1), activation=config['activation']))
    if config['initial_dropout'] > 0:
        model.add(Dropout(config['initial_dropout']))

    # Adds k-1 hidden layers
    for i in range(config['hidden_layers'] - 1):
        model.add(Dense(config['cells_per_layer'], kernel_initializer=config['kernel_initializer'], bias_initializer=initializers.Constant(0.1), activation=config['activation']))
        if config['dropout'] > 0:
            model.add(Dropout(config['dropout']))

    model.add(Dense(output_dim, kernel_initializer='normal'))

    model.compile(loss=config['loss'], optimizer=config['optimizer'], metrics=['mae', 'mse', 'mape', rmse])
    return model


# Save a model to disk
def save_model(model: keras.models.Sequential, config: Config):
    modelpath = model_path(config)
    # Serialize model structure as json file
    model_json = model.to_json()
    if not os.path.isdir(modelpath):
        os.makedirs(modelpath)
    with open(modelpath + 'model.json', 'w') as f:
        f.write(model_json)
    with open(modelpath + 'config.json', 'w') as f:
        f.write(json.dumps(config, indent=4))
    # Serialize model weights as HDF5 file
    model.save_weights(modelpath + 'model.h5')
    print('Model saved: ' + modelpath)


# Load a model from disk
def load_model(config: Config) -> keras.models.Sequential:
    K.clear_session()
    modelpath = model_path(config)
    # Load model structure json
    with open(modelpath + 'model.json', 'r') as json_file:
        loaded_model_json = json_file.read()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into model
    loaded_model.load_weights(modelpath + 'model.h5')
    print('Model loaded: ' + modelpath)
    loaded_model.compile(loss='mean_squared_error', optimizer=config['optimizer'], metrics=['mae', 'mse', 'mape', rmse])
    loaded_model._make_predict_function()
    return loaded_model
