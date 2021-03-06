#!/usr/bin/env python3
from Utils.ReadData import read_data
from Utils.Model import DNNRegressor, save_model, load_model
from Utils.Plot import plot_history
from Utils.Configuration import paths, Config, energy_config
from Utils.Utilities import model_path, printparams, generate_upload_predictions
from tensorflow import set_random_seed
from numpy.random import seed
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from Utils.Metrics import mean_absolute_percentage_error, root_mean_squared_error
import pandas as pd
import time
import json
import os
import sys

seed(1337)  # Numpy seed
set_random_seed(1337)  # TensorFlow seed


def do_speed_predictions_if_not_there(config: Config):
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


def read_predicting_data_sets(config: Config, retain_id: bool, first=False) -> (pd.DataFrame, pd.DataFrame):
    do_speed_predictions_if_not_there(config)

    print("")
    print("------ Reading data ------")
    start_time = time.time()
    if config['supersegment']:
        path_t = paths['supersegTrainPath']
        path_v = paths['supersegValidationPath']
    else:
        path_t = paths['dataPath']
        path_v = None
    X_train, Y_train, train_trip_ids = read_data(path_t, config, retain_id=retain_id, first=first)
    if path_v is not None:
        X_test, Y_test, test_trip_ids = read_data(path_v, config, retain_id=retain_id, first=first)
        X = pd.concat([X_train, X_test], ignore_index=True)
        Y = pd.concat([Y_train, Y_test], ignore_index=True)
        trip_ids = pd.concat([train_trip_ids, test_trip_ids], ignore_index=True)
    else:
        X = X_train
        Y = Y_train
        trip_ids = train_trip_ids
    print("Data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    return X, Y, trip_ids


def read_training_data_sets(config: Config) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame):
    print()
    printparams(config)

    do_speed_predictions_if_not_there(config)

    if config['supersegment']:
        train_path = paths['supersegTrainPath']
        valid_path = paths['supersegValidationPath']
    else:
        train_path = paths['trainPath']
        valid_path = paths['validationPath']

    print("")
    print("------ Reading training data ------")
    start_time = time.time()
    X_train, Y_train, train_trip_ids = read_data(train_path, config, re_scale=True)
    print("Training data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    print("")
    print("------ Reading validation data ------")
    start_time = time.time()
    X_validation, Y_validation, val_trip_ids = read_data(valid_path, config)
    print("Validation data read")
    print("Time elapsed: %s seconds" % (time.time() - start_time))

    return X_train, Y_train, X_validation, Y_validation, train_trip_ids, val_trip_ids


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

    trip_Y = pd.concat([Y[[config['target_feature']]], trip_ids[['trip_id']]], axis=1)\
        .groupby(['trip_id']).sum().sort_values(by=['trip_id'])

    trip_pred = trip_prediction['prediction']
    trip_act = trip_Y[config['target_feature']]

    preds = {'r2': r2,
             'trip_r2': r2_score(trip_act, trip_pred),
             'trip_mae': mean_absolute_error(trip_act, trip_pred),
             'trip_rmse': root_mean_squared_error(trip_act, trip_pred),
             'trip_mse': mean_squared_error(trip_act, trip_pred),
             'trip_mape': mean_absolute_percentage_error(trip_act, trip_pred)}

    #full_df = pd.concat([X, pd.DataFrame(prediction, columns=['prediciton'])], axis=1)
    #full_df = pd.concat([full_df, Y[[config['target_feature']]]], axis=1)
    #full_df['type'] = np.nan
    #for x in list(full_df):
    #    if "type_" in x:
    #        full_df.loc[full_df[x] > 0, ['type']] = x[5:]

    #full_df = full_df[['prediciton', config['target_feature'], 'type', 'incline']]
    #full_df['incline'] = np.floor(full_df['incline'] / 4) * 4
    #grp_type = full_df.groupby(['type'])
    #grp_inc = full_df.groupby(['incline'])

    #dfs_type = {k: df for k, df in grp_type}
    #dfs_inc = {k: df for k, df in grp_inc}

    #for k in dfs_type.keys():
    #    preds[k + "_r2"] = r2_score(dfs_type[k][config['target_feature']], dfs_type[k]['prediciton'])
    #for k in dfs_inc.keys():
    #    preds["Incline_" + str(k) + "-" + str(k+4) + "_r2"] = r2_score(dfs_inc[k][config['target_feature']], dfs_inc[k]['prediciton'])

    print("")
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return pd.DataFrame(prediction, columns=['prediction']), preds


def load_history(config: Config):
    modelpath = model_path(config)
    if not os.path.isfile(modelpath + 'history.json'):
        return None
    with open(modelpath + 'history.json', "r") as f:
        hist = json.loads(f.read())
    return hist


def save_history(history, config: Config):
    modelpath = model_path(config)
    print("")
    print("------ Saving history ------")
    start_time = time.time()
    if not os.path.isdir(modelpath):
        os.makedirs(modelpath)
    with open(modelpath + 'history.json', "w") as f:
        f.write(json.dumps(history, indent=4))
    print("History saved")
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return history


def train(config: Config):
    #model = load_model(config)
    #hist = load_history(config)
    #if model is None or hist is None:
    #    return None

    X_train, Y_train, X_validation, Y_validation, train_trip_ids, val_trip_ids = read_training_data_sets(config)
    model, history = train_model(X_train, Y_train, X_validation, Y_validation, config)
    hist = history.history

    if model is None or hist is None:
        return None

    train_predictions, preds = calculate_results(model, X_train, Y_train, train_trip_ids, config)
    val_predictions, val_preds = calculate_results(model, X_validation, Y_validation, val_trip_ids, config)

    for k in val_preds.keys():
        preds['val_' + k] = val_preds[k]
    for k in [x for x in preds.keys() if 'val' not in x]:
        preds['train_' + k] = preds.pop(k)
    print(preds)

    print()
    print("Segments:")
    print("Train R2: {:f}".format(preds['train_r2']) + "  -  Validation R2: {:f}".format(preds['val_r2']))
    print("Trips:")
    print("Train R2: {:f}".format(preds['train_trip_r2']) + "  -  Validation R2: {:f}".format(preds['val_trip_r2']))
    for k, v in preds.items():
        hist[k] = v
    save_history(hist, config)
    plot_history(hist, config)
    return hist


def predict(config: Config, save_predictions: bool=False, first=False):
    X, Y, trip_ids = read_predicting_data_sets(config, save_predictions, first)

    keys = None
    if save_predictions:
        keys = X['mapmatched_id']
        X.drop(['mapmatched_id'], axis=1, inplace=True)

    model = load_model(config)
    predictions, preds = calculate_results(model, X, Y, trip_ids, config)
    print()
    print("Segments:")
    print("R2-score: {:f}".format(preds['r2']))
    print("Trips:")
    print("R2-score: {:f}".format(preds['trip_r2']))

    #dfm = pd.read_csv("meters.csv")
    #dfm['pred_' + config['model_name_base']] = predictions['prediction']
    #dfm.to_csv("meters.csv", index=False)

    if save_predictions:
        predictions.rename(columns={'0': 'prediction'})
        predictions['mapmatched_id'] = keys
        predictions[['mapmatched_id', 'prediction']].to_csv(model_path(config) + "/predictions.csv", index=False)
        print("Predictions saved to file:" + model_path(config) + "/predictions.csv")
        with open(model_path(config) + "/upload_predictions.sh", "w+") as file: # create script for uploading predictions
            file.write(generate_upload_predictions(model_path(config)))
        print("Created upload_predictions script in model dir, which can be run to upload new predictions to main db")



if __name__ == "__main__":
    args = sys.argv[1:]
    default_config = energy_config

    if len(args) > 0 and args[0] == "predict":
        predict(default_config, True)
    else:
        train(default_config)
