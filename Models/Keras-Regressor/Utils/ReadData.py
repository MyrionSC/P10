from Utils.LocalSettings import main_db
from Utils.SQL import read_query, road_map_qry, average_weather_qry, get_existing_trips
import pandas as pd
import numpy as np
from Utils.Configuration import Config
from Utils.Utilities import model_path, embedding_path, get_cats
from sklearn.preprocessing import StandardScaler
import time
import os
import json
from pandas.api.types import CategoricalDtype
from typing import List


# Reads the road map from database
def read_road_map_data(month, quarter, hour, two_hour, four_hour, six_hour, twelve_hour, weekday):
    qry = road_map_qry()

    qry2 = average_weather_qry(month, quarter)

    print()
    print("------ Reading road map ------")
    start_time = time.time()
    df = pd.DataFrame(read_query(qry, main_db))
    df2 = read_query(qry2, main_db)[0]
    df['temperature'] = df2['temperature']
    df['headwind_speed'] = df2['headwind_speed']
    df['month'] = month
    df['quarter'] = quarter
    df['hour'] = hour
    df['two_hour'] = two_hour
    df['four_hour'] = four_hour
    df['six_hour'] = six_hour
    df['twelve_hour'] = twelve_hour
    df['weekday'] = weekday
    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df.sort_values(['segmentkey', 'direction'])


# Read data from csv file at path
def read_data(path: str, config: Config, re_scale: bool=False, retain_id: bool=False) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    # Get the base data from the csv
    df = get_base_data(path, config)
    return preprocess_data(df, config, re_scale, retain_id)


def get_candidate_trip_data(trip_ids: List[int], config: Config, re_scale: bool=False, retain_id: bool=False) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    df = get_base_data_trips(trip_ids, config)
    return preprocess_data(df, config, re_scale, retain_id)


def preprocess_data(df: pd.DataFrame, config: Config, re_scale: bool=False, retain_id: bool=False) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    # If speed predictions are set to be used, include them
    if 'speed_prediction' in config['features_used']:
        df = get_speed_predictions(df, config['speed_model_path'])

    # One hot encode categorical features
    if 'month' in config['features_used'] or 'weekday' in config['features_used'] \
            or 'categoryid' in config['features_used']:
        df = one_hot(df)

    # Read and merge embeddings into dataframe
    if config['embedding'] is not None:
        df = get_embeddings(df, config)

    trip_ids = df[['trip_id']]

    df.drop(['segmentkey', 'trip_id'], axis=1, inplace=True)
    if not retain_id:
        df.drop(['mapmatched_id'], axis=1, inplace=True)

    # Convert quarter column to a sinusoidal representation if specified
    if config['cyclic_time']:
        df = convert_time(df)

    # Split data into features and label
    features, label = extract_label(df, config)

    # Scale data using a simple sklearn scaler
    keys = None
    if retain_id:
        keys = df['mapmatched_id']
        df.drop(['mapmatched_id'], axis=1, inplace=True)

    if config['scale']:
        features = scale_df(features, config, re_scale)

    if retain_id:
        features['mapmatched_id'] = keys

    return features, label, trip_ids


def get_base_data_trips(trip_ids, config: Config) -> pd.DataFrame:
    print("Reading trip data")
    start_time = time.time()

    df = pd.DataFrame(read_query(get_existing_trips(trip_ids), main_db))

    df = df[['segmentkey', 'mapmatched_id', 'trip_id'] + [config['target_feature']] + [x for x in config['features_used'] if
                                                                                   not x == 'speed_prediction']]

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# Read the base dataframe
def get_base_data(path: str, config: Config) -> pd.DataFrame:
    print("Reading data from " + path)
    start_time = time.time()

    # Read the data from the csv file
    df = pd.read_csv(path, header=0)

    # Remove redundant columns
    df = df[['segmentkey', 'mapmatched_id', 'trip_id'] + [config['target_feature']] + [x for x in config['features_used'] if
                                                                            not x == 'speed_prediction']]

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# Get speed predictions from a file and add them to the dataframe
def get_speed_predictions(df: pd.DataFrame, speed_model_path: str) -> pd.DataFrame:
    print("Reading speed predictions from " + speed_model_path + '/predictions.csv')
    start_time = time.time()

    # Read the speed predictions from the csv file
    speed_df = pd.read_csv(speed_model_path + '/predictions.csv', header=0, sep=',')
    speed_df.rename(columns={'prediction': 'speed_prediction'}, inplace=True)

    # Merge the speed predictions into the main dataframe
    df = df.merge(speed_df, left_on='mapmatched_id', right_on='mapmatched_id')
    df.sort_values('mapmatched_id', inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# One hot encode categorical feature columns
def one_hot(df: pd.DataFrame) -> pd.DataFrame:
    # One-hot encode category, month and weekday columns
    print()
    print("------ One-hot encoding features ------")
    start_time = time.time()

    pd.options.mode.chained_assignment = None

    # If the categorical features are present in the dataframe, encode them
    if 'categoryid' in list(df):
        df['categoryid'] = df['categoryid'].map(str)
        df = one_hot_encode_column(df, 'categoryid')
    if 'month' in list(df):
        df['month'] = df['month'].map(str)
        df = one_hot_encode_column(df, 'month')
    if 'weekday' in list(df):
        df['weekday'] = df['weekday'].map(str)
        df = one_hot_encode_column(df, 'weekday')

    pd.options.mode.chained_assignment = 'warn'

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# One-hot encode a column of a dataframe
def one_hot_encode_column(df: pd.DataFrame, column_key: str) -> pd.DataFrame:
    # Encode column as categorical dtype
    cats = get_cats(column_key)
    cat_type = CategoricalDtype(categories=cats, ordered=True)
    df[column_key] = df[column_key].astype(cat_type)

    # One-hot encode column
    df = pd.concat([df, pd.get_dummies(df[column_key], prefix=column_key)], axis=1)
    df.drop([column_key], axis=1, inplace=True)

    print("Column \'" + column_key + "\' encoded to " + str(len(cats)) + " columns")
    return df


# Get embeddings and add them to the dataframe
def get_embeddings(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    print()
    print("------ Getting embeddings ------")
    print('Reading embeddings from ' + embedding_path(config))
    start_time = time.time()

    # Read embeddings from the csv file
    emb_df = read_embeddings(config)

    print("Merging embeddings")
    # Merge embeddings into main dataframe
    df = df.merge(emb_df, left_on='segmentkey', right_on=emb_df.index)

    # Sort dataframe and drop redundant columns
    if 'mapmatched_id' in list(df):
        df.sort_values('mapmatched_id', inplace=True)
        df.reset_index(drop=True, inplace=True)

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# Read embeddings from disk
def read_embeddings(config: Config) -> pd.DataFrame:
    # Get the number of dimensions of the embeddings
    with open(embedding_path(config), 'r') as f:
        dim = int(f.readline().split(" ")[1].strip())

    # Read the embeddings from the csv file
    df = pd.read_csv(embedding_path(config), header=None, sep=' ', skiprows=1)

    # If the embeddings are generated using LINE, drop the last column
    # This is due to the way LINE saves the embeddings to a file
    if config['embedding'].startswith('LINE'):
        df = df.drop(dim + 1, axis=1)

    # Index dataframe by segmentkey
    df = df.rename(columns={0: 'segmentkey'})
    df = df.set_index(['segmentkey'])

    # Rename columns
    df = df.rename(lambda x: "emb_" + str(x - 1), axis='columns')

    return df


# Convert quarter feature column into a circular sinusoidal representation
def convert_time(df: pd.DataFrame) -> pd.DataFrame:
    possible_values = {
        'quarter': 96,
        'hour': 24,
        'two_hour': 12,
        'four_hour': 6,
        'six_hour': 4,
        'twelve_hour': 2
    }

    targets = [x for x in possible_values.keys() if x in list(df)]

    if len(targets) == 0:
        print("No time interval columns to convert to circular representation")
        return df
    elif len(targets) == 1:
        print("Converting \'" + targets[0] + "\' column to circular representation")
    else:
        print("Converting colums: " + ", ".join(["\'" + x + "\'" for x in targets[:-1]]) + ", and \'" + targets[-1] + "\' to circular representation")

    start_time = time.time()

    for target in targets:
        # Calculate sine and cosine features based on the quarter column
        sin = np.sin(2 * np.pi * df[target] / (possible_values[target] - 1))
        cos = np.cos(2 * np.pi * df[target] / (possible_values[target] - 1))
        df.drop(target, axis=1, inplace=True)
        df['sin_' + target] = sin
        df['cos_' + target] = cos

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# Extract the label column from the features
def extract_label(df: pd.DataFrame, config: Config) -> (pd.DataFrame, pd.DataFrame):
    print("Extracting label")
    start_time = time.time()

    # Extract the target feature from the dataframe
    label = df[[config['target_feature']]]
    df.drop(columns=[config['target_feature']], axis=1, inplace=True)

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed %s\n" % (time.time() - start_time))
    return df, label


# Scale the dataframe
def scale_df(df: pd.DataFrame, config: Config, re_scale=False) -> pd.DataFrame:
    start_time = time.time()

    # Cache the column names of the dataframe.
    columns = list(df)

    # If a scaler exists and creating a new scaler is not explicitly requested, load the existing scaler
    if not re_scale and os.path.isfile(model_path(config) + "scaler.json"):
        scaler = load_scaler(config)
    # Otherwise, create a new scaler
    else:
        scaler = create_scaler(df, config)

    # Scale the dataframe
    df = pd.DataFrame(scaler.transform(df))

    # Reapply the cached column names
    df.rename(lambda x: columns[x], axis='columns', inplace=True)

    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df


# Create a new scaler
def create_scaler(df: pd.DataFrame, config: Config) -> StandardScaler:
    print("Creating scaler in " + model_path(config))
    scaler = StandardScaler()
    scaler.fit(df)
    save_scaler(scaler, config)
    return scaler


# Save the scaler
def save_scaler(scaler: StandardScaler, config: Config):
    modelpath = model_path(config)
    if not os.path.isdir(modelpath):
        os.makedirs(modelpath)

    scaler_params = dict()
    scaler_params['scale_'] = scaler.scale_.tolist()
    scaler_params['mean_'] = scaler.mean_.tolist()
    scaler_params['var_'] = scaler.var_.tolist()
    scaler_params['n_samples_seen_'] = int(scaler.n_samples_seen_)
    scaler_json = json.dumps(scaler_params)

    with open(modelpath + "scaler.json", "w") as f:
        f.write(scaler_json)


# Load an existing scaler
def load_scaler(config: Config) -> StandardScaler:
    modelpath = model_path(config)
    print("Loading scaler from " + modelpath)
    with open(modelpath + "scaler.json", "r") as f:
        scaler_params = json.load(f)

    scaler = StandardScaler()
    scaler.scale_ = np.array(scaler_params['scale_'])
    scaler.mean_ = np.array(scaler_params['mean_'])
    scaler.var_ = np.array(scaler_params['var_'])
    scaler.n_samples_seen_ = scaler_params['n_samples_seen_']
    return scaler
