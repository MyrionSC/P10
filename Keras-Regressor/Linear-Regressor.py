from Utils import plot_history
from Utils import save_model, load_model
from Utils import read_data
from Model import LinearRegressor
from Metrics import *
import pandas as pd
import time
from tensorflow import set_random_seed
from numpy.random import seed
seed(1337) # Numpy seed
set_random_seed(1337) #Tensorflow seed
import os
import json
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from math import sqrt

def load_columns(filename, columns=[], index=None):
    """
        Loads columns  into pandas DataFrame object
        from specified .csv file;

        Args:
            filename (str): name of .csv file
            columns (list): list of columns to load
            index    (str): name of index
        Returns:
            df (pd.DataFrame) : pandas DataFrame with one column (index) set as index
    """
    df = pd.read_csv(filename)
    df = df[columns]

    if index is not None:
        df.set_index('mapmatched_id', inplace=True)

    return df

def root_mean_squared_error(y_true, y_pred):
    return sqrt(mean_squared_error(y_true, y_pred))

train = False
epochs = 10
batch_size = 32768 // 8
dataPath = "../data/Data.csv"
trainPath = "../data/Training.csv"
validationPath = "../data/Validation.csv"
target_feature = ['ev_wh']
remove_features = ['min_from_midnight', 'acceleration', 'deceleration']
# Read the data from the specified CSV file

if train:
    X_train, Y_train, num_features, num_labels, embeddings_used, trip_ids_train \
        = read_data(trainPath, target_feature, remove_features)
    X_validation, Y_validation, _, _, _, trip_ids_validation \
        = read_data(validationPath, target_feature, remove_features)

    history_collection = list()

    # Create estimator
    estimator = LinearRegressor(num_features)

    start_time = time.time()
    # Train estimator and get training history
    history = estimator.fit(X_train, Y_train, epochs=epochs, validation_data=(X_validation, Y_validation), batch_size=batch_size, verbose=1,
                            shuffle=True)
    end_time = time.time()
    print('Time to complete %s epochs: %s seconds with batch size %s' % (epochs, end_time - start_time, batch_size))

    prediction = estimator.predict(X_train, batch_size=batch_size, verbose=1)
    val_prediction = estimator.predict(X_validation, batch_size=batch_size, verbose=1)
    train_r2 = r2_score(Y_train, prediction)
    val_r2 = r2_score(Y_validation, val_prediction)
    train_mae = mean_absolute_error(Y_train, prediction)
    val_mae = mean_absolute_error(Y_validation, val_prediction)
    history.history['train_r2'] = train_r2
    history.history['val_r2'] = val_r2
    history.history['train_mae'] = train_mae
    history.history['val_mae'] = val_mae

    model_output_path = ("saved_models/LinearRegressor %s" % "ev_wh")
    save_model(estimator, model_output_path)
    history_collection.append(history.history)
    print()

    # Save history
    history_output_path = ("saved_history/LinearRegressor predicting %s.json" % "ev_wh")
    if os.path.isdir("saved_history") and os.path.isfile(history_output_path):
        with open(history_output_path) as f:
            history_list = json.load(f)
    else:
        history_list = list()

    history_list.append(history.history)
    history_json = json.dumps(history_list)

    if not os.path.isdir("saved_history"):
        os.makedirs(os.path.dirname(history_output_path))
    with open(history_output_path, "w") as f:
        f.write(history_json)

    for results in history_collection:
        print("Epochs: " + str(epochs) + " Batch size: " + str(batch_size))
        print("Removed features: " + ', '.join(remove_features))
        print("Train R2: {:f}".format(results['train_r2']) + "  -  Validation R2: {:f}".format(results['val_r2']))
        print("Train MAE: {:f}".format(results['train_mae']) + "  -  Validation MAE: {:f}".format(results['val_mae']))

else:
    features, labels, num_features, num_labels, _, trip_ids = read_data(dataPath, target_feature, remove_features)

    # Loads model
    params = dict(batch_size=batch_size,
                  epochs=epochs)

    param_string = ','.join("%s=%s" % (key, value) for (key, value) in params.items())
    target_feature_string = ','.join("%s" % x for x in target_feature)
    embeddings_used_string = ""

    modelPath = ("saved_models/LinearRegressor %s" % "ev_wh")

    model = load_model(modelPath)

    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mse', 'mape', rmse, r2])
    prediction = model.predict(features, batch_size=batch_size, verbose=1)
    evaluation = model.evaluate(features, labels, batch_size=batch_size, verbose=1)

    # go over predictions saving them into pandas DataFrame
    df = load_columns(dataPath, columns=['mapmatched_id', 'segment_length', 'trip_id'])

    for i, target in enumerate(target_feature):
        target_predict = str(target + "_prediction")
        df[target_predict] = pd.Series(prediction[:, i])
        df[target] = labels[target]
        prediction_df = df[['mapmatched_id', target_predict]].copy()
        prediction_file_path = target + "_prediction.csv"
        prediction_df.to_csv(prediction_file_path, index=False)

    column = df.columns

    grouped_df = df.groupby('trip_id')[column[3:]].sum()

    trip_mae = mean_absolute_error(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    trip_rmse = root_mean_squared_error(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    trip_r2 = r2_score(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    segment_mae = mean_absolute_error(df['ev_wh'], df['ev_wh_prediction'])
    segment_rmse = root_mean_squared_error(df['ev_wh'], df['ev_wh_prediction'])
    segment_r2 = r2_score(df['ev_wh'], df['ev_wh_prediction'])
    test = 'a'
