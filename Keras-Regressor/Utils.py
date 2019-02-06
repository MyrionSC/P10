import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import *
from keras.models import model_from_json
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
        df['categoryid'] = df['categoryid'].map(str)
        df = one_hot_encode_column(df, 'categoryid')
    if 'month' not in config['remove_features']:
        df['month'] = df['month'].map(str)
        df = one_hot_encode_column(df, 'month')
    if 'weekday' not in config['remove_features']:
        df['weekday'] = df['weekday'].map(str)
        df = one_hot_encode_column(df, 'weekday')
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))
    return df


def preprocess_data(df):
    df = one_hot(df)
    df = scale_df(df, load_scaler=True)
    return df


# Read data from csv file at path
def read_data(path, target_feature, remove_features, scale=False, load_scaler=False, cyclicquarter=False, use_speed_prediction=False):
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

    # One hot encode categorical features
    df = one_hot(df)

    # Read and merge embeddings into dataframe
    if config['embeddings_used'] is not None:
        emb_df = read_embeddings()
        df = merge_embeddings(df, emb_df)

    # Sort dataframe to avoid null values (no idea why, but it's necessary)
    df = df.sort_values('mapmatched_id').reset_index(drop=True)

    # Remove startpoint and endpoint columns if present
    if 'startpoint' in list(df):
        df = df.drop('startpoint', axis=1)
    if 'endpoint' in list(df):
        df = df.drop('endpoint', axis=1)

    # Convert quarter column to a sinusoidal representation if specified
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
    features = df.drop(columns=target_feature + ['segmentkey', 'mapmatched_id', 'trip_id'])
    print("Time %s" % (time.time() - start_time))

    # Calculate the number of features (input dimension of model)
    num_features = len(list(features))
    num_labels = len(list(label))

    # debug info
    # print('Using following features:')
    # for i, column in enumerate(features):
    #     print('  %d) \'%s\'' % (i, column))

    # Scale data using a simple sklearn scaler
    if scale:
        features = scale_df(features, load_scaler)
        
    return features, label, num_features, num_labels, trip_ids


def scale_df(df, load_scaler=False):
    print("Scaling data sets")
    start_time = time.time()
    columns = list(df)

    if load_scaler:
        scaler = loadScaler(config['target_feature'], config['remove_features'], config['embeddings_used'])
    else:
        scaler = StandardScaler()
        scaler.fit(df)
        saveScaler(scaler, config['target_feature'], config['remove_features'], config['embeddings_used'])

    df = pd.DataFrame(scaler.transform(df))
    df = df.rename(lambda x: columns[x], axis='columns')

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


def read_embeddings():
    print('Importing embeddings from ' + embedding_path())
    start_time = time.time()
    if config['embeddings_used'] == 'LINE':
        start_time = time.time()
        df = pd.read_csv(embedding_path(), header=None, sep=' ', skiprows=1)
        df = df.rename(columns={0: 'segmentkey'})
        df = df.drop(embedding_config['LINE']['dims'] + 1, axis=1)
        df = df.set_index(['segmentkey'])
        df = df.rename(lambda x: "emb_" + str(x-1), axis='columns')
    else:
        df = pd.read_csv(embedding_path(), header=0, sep=' ')
    print("Time %s" % (time.time() - start_time))
    return df


def merge_embeddings(df, emb_df):
    print("Merging data sets")
    start_time = time.time()
    if config['graph_type'] == 'transformed':
        df = pd.merge(df, emb_df, left_on='segmentkey', right_on=emb_df.index)
    elif config['graph_type'] == 'normal':
        df = pd.merge(df, emb_df, left_on='startpoint', right_on='point').drop(['startpoint', 'point'], axis=1)
        df = pd.merge(df, emb_df, left_on='endpoint', right_on='point').drop(['endpoint', 'point'], axis=1)
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))
    return df


def embedding_path():
    return paths[config['embeddings_used']] + config['graph_type'] + "-" + str(embedding_config[config['embeddings_used']]['dims']) + "d.emb"
