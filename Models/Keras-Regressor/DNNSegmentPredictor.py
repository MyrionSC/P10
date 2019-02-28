from Utils import load_model, query, one_hot, read_embeddings
import pandas as pd
from Metrics import rmse
from Configuration import *
import sys
import json
import os

month = '2'
quarter = '47'
weekday = '4'


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
        WHERE osm.category != 'ferry'
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
    df['weekday'] = weekday
    return df.sort_values('segmentkey')


def do_predictions(config, df):
    features = df[['segmentkey'] + config['features_used']]

    if 'month' in config['features_used'] or 'weekday' in config['features_used']\
            or 'categoryid' in config['features_used']:
        features = one_hot(features)

    if config['embedding'] is not None:
        emb_df = read_embeddings(config)
        features = features.merge(emb_df, left_on='segmentkey', right_on=emb_df.index)

    features.sort_values('segmentkey', inplace=True)
    features.set_index(['segmentkey'], inplace=True)

    model = load_model(config)
    model.compile(loss='mean_squared_error', optimizer=config['optimizer'],
                        metrics=['mae', 'mse', 'mape', rmse])

    return pd.DataFrame(model.predict(features, batch_size=config['batch_size'], verbose=1),
                        columns=[config['target_feature'] + '_prediction'])


def create_segment_predictions(config):
    df = read_road_map_data()
    keys = df[['segmentkey']]
    speed_predictions = do_predictions(speed_config, df)
    df['speed_prediction'] = speed_predictions
    energy_predictions = do_predictions(config, df)
    energy_predictions['segmentkey'] = keys
    res = energy_predictions[['segmentkey', 'energy_prediction']]
    res.to_csv(model_path(energy_config) + "segment_predictions.csv", sep=';', header=True, index=False,
               encoding='utf8')


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) > 1:
        print("Invalid number of arguments: " + str(len(args)))
        print("Expected 0 or 1")
        quit()

    if len(args) == 1:
        modelpath = args[0].strip()
        if not os.path.isdir(modelpath):
            print("Specified model does not exist")
            quit()
        print("Loading model configuration")
        with open(modelpath + "config.json", "r") as f:
            config = json.load(f)
    else:
        config = energy_config
    create_segment_predictions(config)
