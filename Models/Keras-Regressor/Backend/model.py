from Utils.ReadData import get_candidate_trip_data
from DNNRegressor import calculate_results
from Utils.Model import model_path, load_model
from Utils.SQL import copy_latest_preds_transaction
from Utils.LocalSettings import main_db
from Utils.Utilities import load_config
from keras import backend as K
import geojson
import pandas as pd
import numpy as np

known_energy_trips = [116699, 91881, 4537, 76966, 52557, 175355, 103715]

current_model = "saved_models/Default_Energy_Models/DefaultEnergy-epochs_20"
config = load_config(current_model)
model = load_model(config)


def trip_prediction(trip):
    X, Y, extras = get_candidate_trip_data([trip], config)
    predictions, _, _ = calculate_results(model, X, Y, extras[['trip_id']], config)
    predictions.rename(columns={'prediction': config['target_feature']}, inplace=True)
    geos = extras['segmentgeo'].map(geojson.loads).values
    props = pd.concat([extras['segment_length'], predictions[config['target_feature']]], axis=1).values.T
    temp = [0 for _ in range(len(props[0]))]
    for i in range(len(props[0])):
        temp[i] = 0 if i == 0 else temp[i-1] + props[1][i]
    props = np.vstack([props, temp])
    for i in range(len(props[0])):
        temp[i] = 0 if i == 0 else temp[i-1] + props[0][i]
    props = np.vstack([props, temp])
    geostrings = [geojson.Feature() for _ in range(len(geos))]
    for i in range(len(geos)):
        geostrings[i] = geojson.Feature(geometry=geos[i],
                                        properties={'cost': props[1][i],
                                                    'agg_cost': props[2][i],
                                                    'length': props[0][i],
                                                    'agg_length': props[3][i]})
    return str(geojson.dumps(geojson.FeatureCollection(geostrings)))


def existing_trips_prediction():
    X, Y, extras = get_candidate_trip_data(known_energy_trips, config, retain_id=True)

    keys = X[['mapmatched_id']]
    X.drop(['mapmatched_id'], axis=1, inplace=True)

    predictions, _, _ = calculate_results(model, X, Y, extras[['trip_id']], config)

    predictions.rename(columns={'0': 'prediction'})
    predictions['id'] = keys['mapmatched_id']
    path = model_path(config) + "/latest_predictions.csv"
    predictions[['id', 'prediction']].to_csv(path, index=False, header=False)
    print("Predictions saved to file:" + path)

    copy_latest_preds_transaction(path, main_db)

    return "Database updated with trip predictions for model: " + current_model


def load_new_model(path):
    global config, model
    config = load_config(path)
    K.clear_session()
    model = load_model(config)
