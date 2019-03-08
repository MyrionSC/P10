#!/usr/bin/env python3
from Utils.ReadData import read_data
from Utils.Model import DNNRegressor, save_model, load_model
from Utils.Plot import plot_history
from Utils.Configuration import paths, Config, energy_config
from Utils.Utilities import model_path, printparams
from tensorflow import set_random_seed
from numpy.random import seed
from sklearn.metrics import r2_score
import pandas as pd
import time
import json
import os
import sys

seed(1337)  # Numpy seed
set_random_seed(1337)  # TensorFlow seed


def read_predicting_data_sets(config: Config, retain_id: bool) -> (pd.DataFrame, pd.DataFrame):
    print("")
    print("------ Reading data ------")
    start_time = time.time()
    X, Y, trip_ids = read_data(paths['dataPath'], config, retain_id=retain_id)
    print("Data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    return X, Y, trip_ids


def read_training_data_sets(config: Config) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame):
    print()
    printparams(config)

    print("")
    print("------ Reading training data ------")
    start_time = time.time()
    X_train, Y_train, trip_ids = read_data(paths['trainPath'], config, re_scale=True)
    print("Training data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    print("")
    print("------ Reading validation data ------")
    start_time = time.time()
    X_validation, Y_validation = read_data(paths['validationPath'], config)
    print("Validation data read")
    print("Time elapsed: %s seconds" % (time.time() - start_time))

    return X_train, Y_train, X_validation, Y_validation, trip_ids


def train_model(X_train: pd.DataFrame, Y_train: pd.DataFrame, X_validation: pd.DataFrame, Y_validation: pd.DataFrame, config: Config):
    print("")
    print("------ Training -----")
    start_time = time.time()

    # Create estimator
    estimator = DNNRegressor(len(list(X_train)), len(list(Y_train)), config)

    # Train estimator and get training history
    history = estimator.fit(X_train, Y_train, epochs=config['epochs'], validation_data=(X_validation, Y_validation),
                            batch_size=config['batch_size'], verbose=1, shuffle=True)
    save_model(estimator, config)

    print("Model trained for %s epochs" % (config['epochs']))
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return estimator, history


def calculate_results(estimator, X: pd.DataFrame, Y: pd.DataFrame, trip_ids: pd.DataFrame, config: Config) -> (pd.DataFrame, float):
    print("")
    print("------ Calculating R2-score ------")
    start_time = time.time()
    prediction = estimator.predict(X, batch_size=config['batch_size'], verbose=1)
    r2 = r2_score(Y, prediction)

    trip_prediction = pd.concat([pd.DataFrame(prediction, columns=['prediction']), trip_ids[['trip_id']]], axis=1)\
        .groupby(['trip_id']).sum().sort_values(by=['trip_id'])

    trip_Y = pd.concat([pd.DataFrame(Y, columns=['true']), trip_ids[['trip_id']]], axis=1)\
        .groupby(['trip_id']).sum().sort_values(by=['trip_id'])

    trip_r2 = r2_score(trip_Y['true'], trip_prediction['prediction'])

    print("")
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return pd.DataFrame(prediction, columns=['prediction']), r2, trip_r2


def save_history(history, config: Config):
    modelpath = model_path(config)
    print("")
    print("------ Saving history ------")
    start_time = time.time()
    if not os.path.isdir(modelpath):
        os.makedirs(modelpath)
    with open(modelpath + 'history.json', "w") as f:
        f.write(json.dumps(history.history, indent=4))
    print("History saved")
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return history


def train(config: Config):
    # If using speed model, before doing anything else, check if speed model exists and predictions are generated
    if 'speed_prediction' in config['features_used']:
        if not os.path.isdir(config['speed_model_path']):
            print("Error: A speed model at the given speed_model_path does not exist: " + config['speed_model_path'])
            exit(1)

        if not os.path.exists(config['speed_model_path'] + '/predictions.csv'):
            print("a prediction file for the given speed model does not exist: " + config['speed_model_path'])
            print("Generating speed model predictions before continuing with training...")

            print(config['speed_model_path'] + "/config.json")
            with open(config['speed_model_path'] + "/config.json") as configFile:
                speed_config = json.load(configFile)
            predict(speed_config, True)

    X_train, Y_train, X_validation, Y_validation, trip_ids = read_training_data_sets(config)
    model, history = train_model(X_train, Y_train, X_validation, Y_validation, config)

    train_predictions, train_r2, train_trip_r2 = calculate_results(model, X_train, Y_train, trip_ids, config)
    val_predictions, val_r2, train_val_r2 = calculate_results(model, X_validation, Y_validation, trip_ids, config)

    print()
    print("Segments:")
    print("Train R2: {:f}".format(train_r2) + "  -  Validation R2: {:f}".format(val_r2))
    print("Trips:")
    print("Train R2: {:f}".format(train_trip_r2) + "  -  Validation R2: {:f}".format(train_val_r2))
    history.history['train_r2'] = train_r2
    history.history['val_r2'] = val_r2
    history.history['train_trip_r2'] = train_trip_r2
    history.history['train_val_r2'] = train_val_r2
    save_history(history, config)
    plot_history(history.history, config)
    return history


def predict(config: Config, save_predictions: bool=False):
    X, Y, trip_ids = read_predicting_data_sets(config, save_predictions)

    keys = None
    if save_predictions:
        keys = X['mapmatched_id']
        X.drop(['mapmatched_id'], axis=1, inplace=True)

    model = load_model(config)
    predictions, r2, trip_r2 = calculate_results(model, X, Y, trip_ids, config)
    print()
    print("Segments:")
    print("R2-score: {:f}".format(r2))
    print("Trips:")
    print("R2-score: {:f}".format(trip_r2))

    if save_predictions:
        predictions.rename(columns={'0': 'prediction'})
        predictions['mapmatched_id'] = keys
        predictions[['mapmatched_id', 'prediction']].to_csv(model_path(config) + "/predictions.csv", index=False)
        print("Predictions saved to file:" + model_path(config) + "/predictions.csv")


if __name__ == "__main__":
    args = sys.argv[1:]
    default_config = energy_config

    if len(args) > 0 and args[0] == "predict":
        predict(default_config)
    else:
        train(default_config)
