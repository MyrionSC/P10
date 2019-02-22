from LocalSettings import main_db
import pandas as pd
import numpy as np
from config import *
from keras.models import model_from_json
from sklearn.preprocessing import StandardScaler
import time
import os
import json
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from pandas.api.types import CategoricalDtype

cat_list = ['10', '11', '15', '16', '20', '21', '25', '26', '30', '31', '35', '40', '45', '50', '55', '60', '65']


def query(str):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(main_db['name'], main_db['user'], main_db['port'], main_db['host'], main_db['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


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
#def plot_history(history, metrics):
#    for metric in metrics + ['loss']:
#        plt.plot(history.history[metric], label='Training')
#        plt.plot(history.history['val_' + metric], label='Validation')
#        plt.title(metric.capitalize() + " History")
#        plt.ylabel(metric.capitalize())
#        plt.xlabel("Epoch")
#        plt.legend()
#        plt.show()
#        plt.clf()


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


def one_hot(df, config):
    # One-hot encode category, month and weekday columns
    print("One-hot encoding features")
    start_time = time.time()
    if 'categoryid' in list(df):
        df['categoryid'] = df['categoryid'].map(str)
        df = one_hot_encode_column(df, 'categoryid')
    if 'month' in list(df):
        df = one_hot_encode_column(df, 'month')
    if 'weekday' in list(df):
        df['weekday'] = df['weekday'].map(str)
        df = one_hot_encode_column(df, 'weekday')
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))
    return df


def preprocess_data(df):
    df = one_hot(df)
    df = scale_df(df)
    return df


# Read data from csv file at path
def read_data(path, target_feature, remove_features, scale=False, re_scale=False, cyclicquarter=False, use_speed_prediction=False):
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
        df = df.merge(speed_df, left_on='mapmatched_id', right_on='mapmatched_id')
        df.sort_values('mapmatched_id', inplace=True)
        df.reset_index(drop=True, inplace=True)
        print("Dataframe shape: %s" % str(df.shape))
        print("Time %s" % (time.time() - start_time))

    # Remove unused features before merging with embeddings
    print("Removing unused features")
    start_time = time.time()
    df.drop(remove_features, axis=1, inplace=True)
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))

    # One hot encode categorical features
    df = one_hot(df, config)

    # Read and merge embeddings into dataframe
    if config['embeddings_used'] is not None:
        emb_df = read_embeddings()
        df = merge_embeddings(df, emb_df)

    # Sort dataframe to avoid null values (no idea why, but it's necessary)
    df.sort_values('mapmatched_id', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Remove startpoint and endpoint columns if present
    if 'startpoint' in list(df):
        df.drop('startpoint', axis=1, inplace=True)
    if 'endpoint' in list(df):
        df.drop('endpoint', axis=1, inplace=True)

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
    df.drop(columns=target_feature + ['segmentkey', 'mapmatched_id', 'trip_id', 'trip_segmentno'], inplace=True)
    print("Time %s" % (time.time() - start_time))

    # Calculate the number of features (input dimension of model)
    num_features = len(list(df))
    num_labels = len(list(label))

    # debug info
    # print('Using following features:')
    # for i, column in enumerate(features):
    #     print('  %d) \'%s\'' % (i, column))

    # Scale data using a simple sklearn scaler
    if scale:
        df = scale_df(df, re_scale)

    print("Dataframe shape: %s" % str(df.shape))
    return df, label, num_features, num_labels, trip_ids


def scale_df(df, re_scale):
    print("Scaling data sets")
    start_time = time.time()
    columns = list(df)

    if not re_scale and os.path.isfile(scaler_path()):
        scaler = loadScaler()
    else:
        scaler = StandardScaler()
        scaler.fit(df)
        saveScaler(scaler)

    df = pd.DataFrame(scaler.transform(df))
    df.rename(lambda x: columns[x], axis='columns', inplace=True)

    print("Time %s" % (time.time() - start_time))
    return df


def saveScaler(scaler):
    if not os.path.isdir(paths['scalerDir']):
        os.makedirs(paths['scalerDir'])
    
    scaler_params = dict()
    scaler_params['scale_'] = scaler.scale_.tolist()
    scaler_params['mean_'] = scaler.mean_.tolist()
    scaler_params['var_'] = scaler.var_.tolist()
    scaler_params['n_samples_seen_'] = int(scaler.n_samples_seen_)
    scaler_json = json.dumps(scaler_params)
    
    with open(scaler_path(), "w") as f:
        f.write(scaler_json)
    print("Saved scaler " + scaler_path())


def loadScaler():
    with open(scaler_path()) as f:
        scaler_params = json.load(f)

    scaler = StandardScaler()
    scaler.scale_ = np.array(scaler_params['scale_'])
    scaler.mean_ = np.array(scaler_params['mean_'])
    scaler.var_ = np.array(scaler_params['var_'])
    scaler.n_samples_seen_ = scaler_params['n_samples_seen_']

    print("Loaded scaler " + scaler_path())
    return scaler


def read_embeddings():
    print('Importing embeddings from ' + embedding_path())
    start_time = time.time()
    with open(embedding_path(), 'r') as f:
        dim = int(f.readline().split(" ")[1].strip())
    df = pd.read_csv(embedding_path(), header=None, sep=' ', skiprows=1)
    df = df.rename(columns={0: 'segmentkey'})
    if paths['embeddingFile'].startswith('LINE'):
        df = df.drop(dim + 1, axis=1)
    df = df.set_index(['segmentkey'])
    df = df.rename(lambda x: "emb_" + str(x-1), axis='columns')
    print("Time %s" % (time.time() - start_time))
    return df


def merge_embeddings(df, emb_df):
    print("Merging data sets")
    start_time = time.time()
    #if config['graph_type'] == 'transformed':
    df = df.merge(emb_df, left_on='segmentkey', right_on=emb_df.index)
    #elif config['graph_type'] == 'normal':
    #    df = pd.merge(df, emb_df, left_on='startpoint', right_on='point').drop(['startpoint', 'point'], axis=1)
    #    df = pd.merge(df, emb_df, left_on='endpoint', right_on='point').drop(['endpoint', 'point'], axis=1)
    print("Dataframe shape: %s" % str(df.shape))
    print("Time %s" % (time.time() - start_time))
    return df


def embedding_path():
    if config["embeddings_used"] is not None:
        return '{0}{1}.emb'.format(paths['embeddingDir'], paths['embeddingFile'])
    else:
        return "None"


def scaler_path():
    return '{0}{1}.json'.format(paths['scalerDir'], config['scaler_name'])


def general_converter(num_segments, limit=None):
    qrt = "SELECT\n\ts1.trip_id,\n\ts1.trip_segmentno as supersegmentno,\n\t"
    qrt += ",\n\t".join(["s{0}.segmentkey as key{0},\n\ts{0}.categoryid as category{0},\n\ts{0}.meters as segment{0}_length".format(i+1) for i in range(num_segments)])
    qrt += ",\n\t" + " + ".join(["s{0}.meters".format(i + 1) for i in range(num_segments)]) + " as supersegment_length\n"
    qrt += "FROM experiments.rmp10_supersegment_info as s1\n"
    qrt += "\n".join(["JOIN experiments.rmp10_supersegment_info as s{1}\nON s{0}.trip_id = s{1}.trip_id \nAND s{1}.trip_segmentno = s{0}.trip_segmentno + 1".format(i, i+1) for i in range(1, num_segments)])
    qrt += "\nORDER BY trip_id, supersegmentno"
    if limit is not None and isinstance(limit, int):
        qrt += "\nLIMIT " + str(limit)

    df = pd.DataFrame(query(qrt))

    for cat in cat_list:
        df['categoryid_' + cat] = df['segment1_length'] * df['category1'].map(lambda x: 1 if x == int(cat) else 0)
        for i in range(2, num_segments+1):
            df['categoryid_' + cat] = df['categoryid_' + cat] + df['segment' + str(i) + '_length'] * df['category' + str(i)].map(lambda x: 1 if x == int(cat) else 0)
        df['categoryid_' + cat] = df['categoryid_' + cat] / df['supersegment_length']

    for i in range(1, num_segments+1):
        df = df.drop(['segment' + str(i) + '_length', 'category' + str(i)], axis=1)

    return df.set_index(['trip_id', 'supersegmentno'])


def cat_converter():
    df = pd.DataFrame(query(qry))
    for cat in cat_list:
        df[cat] = (df['segment1_length'] * df['category1'].map(lambda x: 1 if x == int(cat) else 0) +
                  df['segment2_length'] * df['category2'].map(lambda x: 1 if x == int(cat) else 0) +
                  df['segment3_length'] * df['category3'].map(lambda x: 1 if x == int(cat) else 0)) / \
                  df['supersegment_length']

    df = df.drop(['segment1_length', 'segment2_length', 'segment3_length', 'category1', 'category2', 'category3'], axis=1)
    print('hej')
