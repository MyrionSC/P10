import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import *
from keras.models import model_from_json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import time
import os
import json
import datetime

from pandas.api.types import CategoricalDtype

# One-hot encode a column of a dataframe
def one_hot_encode_column(dataframe, column_key):
    if column_key == 'categoryid':
        cat_type = CategoricalDtype(categories=['10', '11', '15', '16', '20', '21', '25', '26', '30', '31', '35', '40', '45', '50', '55', '60', '65'],
                                    ordered=True)
        dataframe['categoryid'] = dataframe['categoryid'].astype(cat_type)
    elif column_key == 'month':
        cat_type = CategoricalDtype(categories=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                                    ordered=True)
        dataframe['month'] = dataframe['month'].astype(cat_type)
    elif column_key == 'weekday':
        cat_type = CategoricalDtype(categories=['1', '2', '3', '4', '5', '6', '7'],
                                    ordered=True)
        dataframe['weekday'] = dataframe['weekday'].astype(cat_type)

    dataframe = pd.concat([dataframe, pd.get_dummies(dataframe[column_key], prefix=column_key)], axis=1)
    dataframe.drop([column_key], axis=1, inplace=True)

    # debug info
    print('\'%s\' was encoded as:' % column_key)
    for i, column in enumerate(dataframe.columns):
        if column.startswith(column_key):
            print('  %d) \'%s\'' % (i, column))

    return dataframe


# Plot metrics from a training history
def plot_history(history, metrics):
    for metric in metrics + ['loss']:
        plt.plot(history.history[metric], label='Training')
        plt.plot(history.history['val_' + metric], label='Validation')
        plt.title(metric.capitalize() + " History")
        plt.ylabel(metric.capitalize())
        plt.xlabel("Epoch")
        plt.legend()
        plt.show()
        plt.clf()


# Save a model to disk
def save_model(model, filename):
    # Serialize model structure as json file
    model_json = model.to_json()
    if not os.path.isdir("saved_models"):
        os.makedirs(os.path.dirname(filename))
    with open(filename + '.json', 'w') as f:
        f.write(model_json)

    # Serialize model weights as HDF5 file
    model.save_weights(filename + '.h5')
    print('Model saved: ' + filename + '!')


# Load a model from disk
def load_model(filename):
    # Load model structure json
    with open(filename + '.json', 'r') as json_file:
        loaded_model_json = json_file.read()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into model
    loaded_model.load_weights(filename + '.h5')
    print('Model loaded: ' + filename + '!')
    return loaded_model


def current_time():
    now = datetime.datetime.today()
    return str(now.month), str(now.weekday()), str((now.hour * 4) + int(now.minute / 15))


def one_hot(df):
    # One-hot encode category, month and weekday columns
    print("One-hot encoding features")
    start_time = time.time()
    if 'categoryid' not in config['remove_features']:
        df = one_hot_encode_column(df, 'categoryid')
    if 'month' not in config['remove_features']:
        df = one_hot_encode_column(df, 'month')
    if 'weekday' not in config['remove_features']:
        df = one_hot_encode_column(df, 'weekday')
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))
    return df


def preprocess_data(df):
    df = one_hot(df)
    df = scale_df(df, load_scaler=True)
    return df


# Read data from csv file at path
def read_data(path, target_feature, remove_features, emb_transformed_path="", emb_normal_path="", scale=False, load_scaler=False, cyclicquarter=False, use_speed_prediction=False):
    # Read data
    print("Importing data set")
    start_time = time.time()
    df = pd.read_csv(path, header=0)
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))

    if use_speed_prediction:
        print("Importing speed predictions")
        start_time = time.time()
        speed_df = pd.read_csv("../data/speed_prediction.csv", header=0, sep=',')
        print("Time %s" % (time.time() - start_time))

        print("Merging speed predictions")
        start_time = time.time()
        df = pd.merge(df, speed_df, left_on='mapmatched_id', right_on='mapmatched_id')
        df = df.sort_values('mapmatched_id').reset_index(drop=True)
        print("Dataframe shape: %s" % str(df.shape))
        print("Time %s" % (time.time() - start_time))

    # Remove unused features before merging with embeddings
    print("Removing unused features")
    start_time = time.time()
    df = df.drop(remove_features, axis=1)
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))

    df = one_hot(df)

    # If path to transformed embeddings is supplied, import and merge with regular data
    embeddings_used = list()
    if emb_transformed_path != "":
        print("Importing transformed embedded data set")
        start_time = time.time()
        emb_df = pd.read_csv(emb_transformed_path, header=0, sep=' ')
        print("Time %s" % (time.time() - start_time))

        print("Merging data sets")
        start_time = time.time()
        df = pd.merge(df, emb_df, left_on='segmentkey', right_on='segmentkey')
        df = df.sort_values('mapmatched_id').reset_index(drop=True)
        print("Dataframe shape: %s" % str(df.shape))
        print("Time %s" % (time.time() - start_time))
        if emb_transformed_path == "../data/osm_dk_20140101-transformed-64d.emb":
            embeddings_used.append("transformed64")
        if emb_transformed_path == "../data/osm_dk_20140101-transformed-32d.emb":
            embeddings_used.append("transformed32")

    # If path to normal embeddings is supplied, import and merge with regular data
    if emb_normal_path != "":
        print("Importing normal embedded data set")
        start_time = time.time()
        emb_df = pd.read_csv(emb_normal_path, header=0, sep=' ')
        print("Time %s" % (time.time() - start_time))

        print("Merging data sets")
        start_time = time.time()
        df = pd.merge(df, emb_df, left_on='startpoint', right_on='point').drop(['startpoint', 'point'], axis=1)
        df = pd.merge(df, emb_df, left_on='endpoint', right_on='point').drop(['endpoint', 'point'], axis=1)
        df = df.sort_values('mapmatched_id').reset_index(drop=True)
        print("Dataframe shape: %s" % str(df.shape))
        print("Time %s" % (time.time() - start_time))
        if emb_normal_path == "../data/osm_dk_20140101-normal-32d.emb":
            embeddings_used.append("normal32")
    else:
        df = df.drop(['startpoint', 'endpoint'], axis=1)

    if cyclicquarter:
        sin = np.sin(2 * np.pi * df['quarter']/95.0)
        cos = np.cos(2 * np.pi * df['quarter']/95.0)
        df = df.drop('quarter',axis=1)
        df['sin_quarter'] = sin
        df['cos_quarter'] = cos


    # Split data into features and label
    print("Splitting data set to features and labels")
    start_time = time.time()
    label = df[target_feature]
    trip_ids = df['trip_id']
    features = df.drop(target_feature, axis=1).drop('segmentkey', axis=1).drop('mapmatched_id', axis=1).drop('trip_id', axis=1)
    print("Time %s" % (time.time() - start_time))

    # Calculate the number of features (input dimension of model)
    num_features = len(list(features))
    num_labels = len(list(label))

    # debug info
    # print('Using following features:')
    # for i, column in enumerate(features):
    #     print('  %d) \'%s\'' % (i, column))

    X_train = features
    Y_train = label

    if scale:
        X_train = scale_df(X_train)
        
    return X_train, Y_train, num_features, num_labels, embeddings_used, trip_ids


def scale_df(df, load_scaler=True):
    print("Scaling data sets")
    start_time = time.time()

    if load_scaler:
        scaler = loadScaler(config['target_feature'], config['remove_features'], config['embeddings_used'])
    else:
        scaler = StandardScaler()
        scaler.fit(df)
        saveScaler(scaler, config['target_feature'], config['remove_features'], config['embeddings_used'])

    df = scaler.transform(df)

    print("Time %s" % (time.time() - start_time))
    return df


def saveScaler(scaler, target_feature, remove_features, embeddings_used):
    if len(embeddings_used) > 0:
        embeddings_used_string = ','.join("%s" % x for x in embeddings_used)
    else:
        embeddings_used_string = "None"
    target_feature_string = ','.join("%s" % x for x in target_feature)
    remove_features_string = ','.join("%s" % x for x in remove_features)
    scaler_path = ("saved_scaler/Scaler - Target features=%s - Removed features=%s - Embeddings=%s.json" % (target_feature_string, remove_features_string, embeddings_used_string))
    
    if not os.path.isdir("saved_scaler"):
        os.makedirs("saved_scaler")
    
    scaler_params = dict()
    scaler_params['scale_'] = scaler.scale_.tolist()
    scaler_params['mean_'] = scaler.mean_.tolist()
    scaler_params['var_'] = scaler.var_.tolist()
    scaler_params['n_samples_seen_'] = int(scaler.n_samples_seen_)
    scaler_json = json.dumps(scaler_params)
    
    with open(scaler_path, "w") as f:
        f.write(scaler_json)


def loadScaler(target_feature, remove_features, embeddings_used):
    if len(embeddings_used) > 0:
        embeddings_used_string = ','.join("%s" % x for x in embeddings_used)
    else:
        embeddings_used_string = "None"
    target_feature_string = ','.join("%s" % x for x in target_feature)
    remove_features_string = ','.join("%s" % x for x in remove_features)
    scaler_path = ("saved_scaler/Scaler - Target features=%s - Removed features=%s - Embeddings=%s.json" % (target_feature_string, remove_features_string, embeddings_used_string))

    with open(scaler_path) as f:
        scaler_params = json.load(f)

    scaler = StandardScaler()
    scaler.scale_ = np.array(scaler_params['scale_'])
    scaler.mean_ = np.array(scaler_params['mean_'])
    scaler.var_ = np.array(scaler_params['var_'])
    scaler.n_samples_seen_ = scaler_params['n_samples_seen_']

    return scaler
