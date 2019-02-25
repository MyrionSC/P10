from Utils import read_data, load_model, query, one_hot, read_embeddings, merge_embeddings
from config import *
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from math import sqrt
import pandas as pd
from Metrics import rmse
import os
import json
from config import *

month = '2'
quarter = '47'


def read_road_map_data():
    qry = """
        SELECT 
            osm.segmentkey,
            CASE WHEN inc.incline IS NOT NULL 
                 THEN inc.incline
                 ELSE 0 
            END as incline,
            osm.meters as segment_length, 
            sl.speedlimit, 
            osm.categoryid
        FROM maps.osm_dk_20140101 osm
        FULL OUTER JOIN experiments.mi904e18_speedlimits sl
        ON sl.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.mi904e18_segment_incline inc
        ON inc.segmentkey = osm.segmentkey
    """

    qry2 = """
        SELECT
            avg(air_temperature) as temperature
        FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
        JOIN dims.dimdate dat
        ON vit.datekey = dat.datekey
        JOIN dims.dimtime tim
        ON vit.timekey = tim.timekey
        JOIN dims.dimweathermeasure wea
        ON vit.weathermeasurekey = wea.weathermeasurekey
        WHERE dat.month = {0}
        AND tim.quarter = {1}
    """.format(month, quarter)

    df = pd.DataFrame(query(qry))
    df['temperature'] = query(qry2)[0]['temperature']
    df['month'] = month
    df['quarter'] = quarter
    return df.sort_values('segmentkey')


def do_speed_predictions(df, emb_df):
    speed_features = df[['segmentkey'] + speed_config['feature_order']]
    speed_features = one_hot(speed_features, speed_config)
    speed_features = merge_embeddings(speed_features, emb_df)
    speed_features.sort_values('segmentkey', inplace=True)
    speed_features.set_index(['segmentkey'], inplace=True)
    speed_model = load_model(paths['modelDir'] + speed_config['model_name'])
    speed_model.compile(loss='mean_squared_error', optimizer=speed_config['optimizer'],
                        metrics=['mae', 'mse', 'mape', rmse])
    return pd.DataFrame(speed_model.predict(speed_features, batch_size=speed_config['batch_size'], verbose=1),
                        columns=['speed_prediction'])


def do_energy_predictions(df, emb_df, speed_df):
    df['speed_prediction'] = speed_df['speed_prediction']
    energy_features = df[['segmentkey'] + energy_config['feature_order']]
    energy_features = one_hot(energy_features, energy_config)
    energy_features = merge_embeddings(energy_features, emb_df)
    energy_features.sort_values('segmentkey', inplace=True)
    energy_features.set_index(['segmentkey'], inplace=True)
    energy_model = load_model(paths['modelDir'] + energy_config['model_name'])
    energy_model.compile(loss='mean_squared_error', optimizer=energy_config['optimizer'],
                         metrics=['mae', 'mse', 'mape', rmse])
    return pd.DataFrame(energy_model.predict(energy_features, batch_size=energy_config['batch_size'], verbose=1),
                        columns=['energy_prediction'])


df = read_road_map_data()
keys = df[['segmentkey']]
emb_df = read_embeddings()
speed_predictions = do_speed_predictions(df, emb_df)
energy_predictions = do_energy_predictions(df, emb_df, speed_predictions)
energy_predictions['segmentkey'] = keys
res = energy_predictions[['segmentkey', 'energy_prediction']]
res.to_csv("../data/energy_predictions.csv", sep=';', header=False, index=False, encoding='utf8')
