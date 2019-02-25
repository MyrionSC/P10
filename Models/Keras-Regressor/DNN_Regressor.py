from Utils import save_model, read_data, load_model
from Model import DNNRegressor
import Configuration
from Configuration import paths
from tensorflow import set_random_seed
from numpy.random import seed
from sklearn.metrics import r2_score
import time
import json
import os
import sys

seed(1337)  # Numpy seed
set_random_seed(1337)  # TensorFlow seed


def read_predicting_data_sets(config):
    print("")
    print("------ Reading data ------")
    start_time = time.time()
    X, Y = read_data(paths['dataPath'], config, scale=True, use_speed_prediction=not Configuration.speed_predictor)
    print("Data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    return X, Y


def read_training_data_sets(config):
    print("")
    print("------ Reading training data ------")
    start_time = time.time()
    X_train, Y_train = read_data(paths['trainPath'], config, scale=True, re_scale=True, use_speed_prediction=not Configuration.speed_predictor)
    print("Training data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    print("")
    print("------ Reading validation data ------")
    start_time = time.time()
    X_validation, Y_validation = read_data(paths['validationPath'], config, scale=True, use_speed_prediction=not Configuration.speed_predictor)
    print("Validation data read")
    print("Time elapsed: %s seconds" % (time.time() - start_time))

    return X_train, Y_train, X_validation, Y_validation


def train_model(X_train, Y_train, X_validation, Y_validation, config):
    print("")
    print("------ Training -----")
    start_time = time.time()

    # Create estimator
    estimator = DNNRegressor(len(list(X_train)), len(list(Y_train)), config['hidden_layers'], config['cells_per_layer'],
                             config['activation'], config['kernel_initializer'], config['optimizer'],
                             config['initial_dropout'], config['dropout'])

    # Train estimator and get training history
    history = estimator.fit(X_train, Y_train, epochs=config['epochs'], validation_data=(X_validation, Y_validation),
                            batch_size=config['batch_size'], verbose=1, shuffle=True)
    save_model(estimator, config)

    print("Model trained for %s epochs" % (config['epochs']))
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return estimator, history


def calculate_results(estimator, X, Y, config):
    print("")
    print("------ Calculating R2-score ------")
    start_time = time.time()
    prediction = estimator.predict(X, batch_size=config['batch_size'], verbose=1)
    r2 = r2_score(Y, prediction)
    print("")
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return prediction, r2


def save_history(history, train_r2, val_r2, config):
    print("")
    print("------ Saving history ------")
    start_time = time.time()
    history.history['train_r2'] = train_r2
    history.history['val_r2'] = val_r2
    if not os.path.isdir(paths['historyDir']):
        os.makedirs(paths['historyDir'])
    with open(paths['historyDir'] + Configuration.model_name(config) + '_History.json', "w") as f:
        f.write(json.dumps(Configuration, indent=4))
        f.write(json.dumps(history.history, indent=4))
    print("History saved")
    print("Time elapsed: %s seconds" % (time.time() - start_time))


def training(config):
    X_train, Y_train, X_validation, Y_validation = read_training_data_sets(config)
    model, history = train_model(X_train, Y_train, X_validation, Y_validation, config)
    train_predictions, train_r2 = calculate_results(model, X_train, Y_train, config)
    val_predictions, val_r2 = calculate_results(model, X_validation, Y_validation, config)
    print("")
    print("Train R2: {:f}".format(train_r2) + "  -  Validation R2: {:f}".format(val_r2))
    save_history(train_r2, val_r2, history, config)


def predicting(config):
    X, Y = read_predicting_data_sets(config)
    model = load_model(config)
    predictions, r2 = calculate_results(model, X, Y, config)
    print("")
    print("R2-score: {:f}".format(r2))


if __name__ == "__main__":
    args = sys.argv[1:]
    train = True
    if len(args) > 0 and args[0] == "predict":
        train = False

    default_config = Configuration.energy_config

    if train:
        training(default_config)
    else:
        predicting(default_config)
