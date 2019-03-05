from LocalSettings import main_db
import pandas as pd
import numpy as np
from Configuration import paths, model_path, Config, speed_config
import keras
from keras.models import model_from_json
from sklearn.preprocessing import StandardScaler
import time
import os
import json
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from pandas.api.types import CategoricalDtype
from Metrics import rmse
from typing import List


# Execute a query against the database
def query(qry: str):
    conn = psycopg2.connect(
        "dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(main_db['name'], main_db['user'],
                                                                              main_db['port'], main_db['host'],
                                                                              main_db['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(qry)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


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
    modelpath = model_path(config)
    # Load model structure json
    with open(modelpath + 'model.json', 'r') as json_file:
        loaded_model_json = json_file.read()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into model
    loaded_model.load_weights(modelpath + 'model.h5')
    print('Model loaded: ' + modelpath)
    loaded_model.compile(loss='mean_squared_error', optimizer=config['optimizer'], metrics=['mae', 'mse', 'mape', rmse])
    return loaded_model


# Read data from csv file at path
def read_data(path: str, config: Config, re_scale: bool=False, retain_id: bool=False) -> (pd.DataFrame, pd.DataFrame):
    # Get the base data from the csv
    df = get_base_data(path, config)

    # If speed predictions are set to be used, include them
    if 'speed_prediction' in config['features_used']:
        df = get_speed_predictions(df, config['speed_model_path'])

    # One hot encode categorical features
    if 'month' in config['features_used'] or 'weekday' in config['features_used']\
            or 'categoryid' in config['features_used']:
        df = one_hot(df)

    # Read and merge embeddings into dataframe
    if config['embedding'] is not None:
        df = get_embeddings(df, config)

    df.drop(['segmentkey'], axis=1, inplace=True)
    if not retain_id:
        df.drop(['mapmatched_id'], axis=1, inplace=True)

    # Convert quarter column to a sinusoidal representation if specified
    if config['cyclic_quarter']:
        df = convert_quarter(df)

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

    return features, label


# Read the base dataframe
def get_base_data(path: str, config: Config) -> pd.DataFrame:
    print("Reading data from " + path)
    start_time = time.time()

    # Read the data from the csv file
    df = pd.read_csv(path, header=0)

    # Remove redundant columns
    df = df[['segmentkey', 'mapmatched_id'] + [config['target_feature']] + [x for x in config['features_used'] if
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


# Get the possible categories of a feature based on the column key
def get_cats(key: str) -> List[str]:
    if key == 'categoryid':
        return ['10', '11', '15', '16', '20', '21', '25', '26', '30', '31', '35', '40', '45', '50', '55', '60', '65']
    elif key == 'month':
        return ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    elif key == 'weekday':
        return ['1', '2', '3', '4', '5', '6', '7']


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
def convert_quarter(df: pd.DataFrame) -> pd.DataFrame:
    print("Converting \'quarter\' column to circular representation")
    start_time = time.time()

    # Calculate sine and cosine features based on the quarter column
    sin = np.sin(2 * np.pi * df['quarter'] / 95.0)
    cos = np.cos(2 * np.pi * df['quarter'] / 95.0)
    df.drop('quarter', axis=1, inplace=True)
    df['sin_quarter'] = sin
    df['cos_quarter'] = cos

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


# Return the path to the embeddings
def embedding_path(config: Config) -> str:
    if config["embedding"] is not None:
        return '{0}{1}.emb'.format(paths['embeddingDir'], config['embedding'])
    else:
        return "None"


def printparams(config: Config):
    print("Parameters used:")
    for key in sorted(config):
        print(" - " + key + ": " + str(config[key]))
    print()


# Return the current month, weekday and quarter from midnight
def current_time() -> (str, str, str):
    now = datetime.datetime.today()
    return str(now.month), str(now.weekday()), str((now.hour * 4) + int(now.minute / 15))


def read_road_map_data(month, quarter, weekday):
    qry = """
        SELECT 
            osm.segmentkey,
            CASE WHEN inc.incline IS NOT NULL 
                 THEN inc.incline
                 ELSE 0 
            END as height_change,
            CASE WHEN inc.incline IS NOT NULL
                 THEN inc.incline_percentage
                 ELSE 0
            END as incline,
            'FORWARD' as direction,
            osm.meters as segment_length, 
            sl.speedlimit, 
            osm.categoryid,
            CASE WHEN inter.intersection THEN 1 ELSE 0 END as intersection
        FROM maps.osm_dk_20140101 osm
        FULL OUTER JOIN experiments.mi904e18_speedlimits sl
        ON sl.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.mi904e18_segment_incline inc
        ON inc.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.rmp10_intersections inter
        ON inter.segmentkey = osm.segmentkey
        WHERE osm.category != 'ferry'
        UNION
        SELECT 
            osm.segmentkey,
            CASE WHEN inc.incline IS NOT NULL 
                 THEN -inc.incline
                 ELSE 0 
            END as height_change,
            CASE WHEN inc.incline IS NOT NULL
                 THEN -inc.incline_percentage
                 ELSE 0
            END as incline,
            'BACKWARD' as direction,
            osm.meters as segment_length, 
            sl.speedlimit, 
            osm.categoryid,
            CASE WHEN inter.intersection THEN 1 ELSE 0 END as intersection
        FROM maps.osm_dk_20140101 osm
        FULL OUTER JOIN experiments.mi904e18_speedlimits sl
        ON sl.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.mi904e18_segment_incline inc
        ON inc.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.rmp10_intersections inter
        ON inter.segmentkey = osm.segmentkey
        WHERE osm.category != 'ferry' AND osm.direction = 'BOTH'
    """

    qry2 = """
        SELECT
            avg(air_temperature) as temperature,
            avg(-wind.tailwind_magnitude) as headwind_speed
        FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
        JOIN experiments.mi904e18_wind_vectors wind
        ON wind.vector_id = vit.id
        JOIN dims.dimdate dat
        ON vit.datekey = dat.datekey
        JOIN dims.dimtime tim
        ON vit.timekey = tim.timekey
        JOIN dims.dimweathermeasure wea
        ON vit.weathermeasurekey = wea.weathermeasurekey
        WHERE dat.month = {0}
        AND tim.quarter = {1}
    """.format(month, quarter)

    print()
    print("------ Reading road map ------")
    start_time = time.time()
    df = pd.DataFrame(query(qry))
    df2 = query(qry2)[0]
    df['temperature'] = df2['temperature']
    df['headwind_speed'] = df2['headwind_speed']
    df['month'] = month
    df['quarter'] = quarter
    df['weekday'] = weekday
    print("Dataframe shape: %s" % str(df.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return df.sort_values(['segmentkey', 'direction'])


def general_converter(num_segments, limit=None):
    qrt = "SELECT\n\ts1.trip_id,\n\ts1.trip_segmentno as supersegmentno,\n\t"
    qrt += ",\n\t".join([
        "s{0}.segmentkey as key{0},\n\ts{0}.categoryid as category{0},\n\ts{0}.meters as segment{0}_length".format(
            i + 1) for i in range(num_segments)])
    qrt += ",\n\t" + " + ".join(
        ["s{0}.meters".format(i + 1) for i in range(num_segments)]) + " as supersegment_length\n"
    qrt += "FROM experiments.rmp10_supersegment_info as s1\n"
    qrt += "\n".join([
        "JOIN experiments.rmp10_supersegment_info as s{1}\nON s{0}.trip_id = s{1}.trip_id \nAND s{1}.trip_segmentno = s{0}.trip_segmentno + 1".format(
            i, i + 1) for i in range(1, num_segments)])
    qrt += "\nORDER BY trip_id, supersegmentno"
    if limit is not None and isinstance(limit, int):
        qrt += "\nLIMIT " + str(limit)

    df = pd.DataFrame(query(qrt))

    for cat in get_cats('categoryid'):
        df['categoryid_' + cat] = df['segment1_length'] * df['category1'].map(lambda x: 1 if x == int(cat) else 0)
        for i in range(2, num_segments + 1):
            df['categoryid_' + cat] = df['categoryid_' + cat] + df['segment' + str(i) + '_length'] * df[
                'category' + str(i)].map(lambda x: 1 if x == int(cat) else 0)
        df['categoryid_' + cat] = df['categoryid_' + cat] / df['supersegment_length']

    for i in range(1, num_segments + 1):
        df = df.drop(['segment' + str(i) + '_length', 'category' + str(i)], axis=1)

    return df.set_index(['trip_id', 'supersegmentno'])
