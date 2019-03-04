#!/usr/bin/env python3
from Utils import load_model, one_hot, get_embeddings, read_road_map_data, scale_df
import pandas as pd
from Configuration import *
import sys
import json
import os
import time
import errno

month = '2'
quarter = '47'
weekday = '4'


def do_predictions(config, df):
    print()
    print("------ Removing redundant columns ------")
    start_time = time.time()
    features = df[['segmentkey', 'direction'] + config['features_used']]
    print("Dataframe shape: %s" % str(features.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))

    if 'month' in config['features_used'] or 'weekday' in config['features_used']\
            or 'categoryid' in config['features_used']:
        features = one_hot(features)

    if config['embedding'] is not None:
        features = get_embeddings(features, config)

    print()
    print("------ Reindexing ------")
    start_time = time.time()
    features.sort_values(['segmentkey', 'direction'], inplace=True)
    features.set_index(['segmentkey', 'direction'], inplace=True)
    print("Dataframe shape: %s" % str(features.shape))
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))

    if config['scale']:
        features = scale_df(features, config)

    print()
    print("------ Predicting " + config['target_feature'] + " ------")
    start_time = time.time()
    model = load_model(config)
    res = pd.DataFrame(model.predict(features, batch_size=config['batch_size'], verbose=1),
                        columns=[config['target_feature'] + '_prediction'])
    print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    return res


def create_segment_predictions(config):
    df = read_road_map_data(month, quarter, weekday)
    keys = df[['segmentkey', 'direction']]
    if 'speed_prediction' in config['features_used']:
        speed_predictions = do_predictions(speed_config, df)
        df['speed_prediction'] = speed_predictions
    energy_predictions = do_predictions(config, df)
    energy_predictions[['segmentkey', 'direction']] = keys
    res = energy_predictions[['segmentkey', 'direction', config['target_feature'] + '_prediction']]
    res.to_csv(model_path(config) + "segment_predictions.csv", sep=';', header=True, index=False,
               encoding='utf8')


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) > 1:
        print("Invalid number of arguments: " + str(len(args)))
        print("Expected 0 or 1")
        exit(errno.E2BIG)

    if len(args) == 1:
        modelpath = args[0].strip()
        if not os.path.isdir(modelpath):
            print("Specified model does not exist")
            exit(errno.ENOENT)
        with open(modelpath + "config.json", "r") as f:
            config = json.load(f)
    else:
        config = energy_config
    create_segment_predictions(config)
