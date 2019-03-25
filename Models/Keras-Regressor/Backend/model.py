
from Utils.ReadData import get_candidate_trip_data
from DNNRegressor import calculate_results
from Utils.Model import model_path, load_model
from Utils.SQL import copy_latest_preds_transaction
from Utils.LocalSettings import main_db
from Utils.Utilities import load_config
from Backend.db import get_baseline_and_actual
import math
import geojson
import pandas as pd
import numpy as np
from Utils.Errors import TripNotFoundError
from DNNSegmentPredictor import create_segment_predictions, create_trip_predictions

known_energy_trips = [116699, 91881, 4537, 76966, 52557, 175355, 103715]
current_model = "saved_models/Default_Energy_Models/DefaultEnergy-epochs_20"
config = load_config(current_model)
model = load_model(config)


def do_segment_predictions(segments, directions):
    geos, lengths, preds = create_segment_predictions(config, segments, directions)
    return geojsonify(geos, lengths, preds)


def do_trip_predictions(trip_id):
    geos, lengths, preds, keys = create_trip_predictions(config, trip_id)
    return geojsonify(geos, lengths, preds, keys, trip_id)


def geojsonify(geostrings: pd.Series, segment_lengths: pd.Series, predictions: pd.Series, keys=None, trip_id=None):
    geos = geostrings.map(geojson.loads).values
    props = pd.concat([segment_lengths, predictions], axis=1).values.T
    if keys is not None:
        seg_keys = keys.values.T
    else:
        seg_keys = []
    temp = [0 for _ in range(len(props[0]))]
    for i in range(len(props[0])):
        temp[i] = props[1][i] if i == 0 else temp[i - 1] + props[1][i]
    props = np.vstack([props, temp])
    for i in range(len(props[0])):
        temp[i] = props[0][i] if i == 0 else temp[i - 1] + props[0][i]
    props = np.vstack([props, temp])
    other_preds_df = None
    if trip_id is not None:
        other_preds_df = get_baseline_and_actual(trip_id)
    geostrings = [geojson.Feature() for _ in range(len(geos))]
    for i in range(len(geos)):
        properties = {'cost': props[1][i],
                      'agg_cost': props[2][i],
                      'length': props[0][i],
                      'agg_length': props[3][i]}
        if keys is not None:
            properties.update({
                'segmentkey': seg_keys[0][i],
                'direction': seg_keys[1][i]
            })
        if trip_id is not None:
            properties.update({
                'baseline': other_preds_df['baseline'][i],
                'agg_baseline': other_preds_df['agg_baseline'][i],
                'actual': other_preds_df['actual'][i] if math.isnan(other_preds_df['actual'][i]) is not True else 0,
                'agg_actual': other_preds_df['agg_actual'][i]
            })
        geostrings[i] = geojson.Feature(geometry=geos[i],
                                        properties=properties)

    return str(geojson.dumps(geojson.FeatureCollection(geostrings)))

def trip_prediction(trip):
    try:
        X, Y, extras = get_candidate_trip_data([trip], config)
    except TripNotFoundError as e:
        print(e)
        raise e
    predictions, _, _ = calculate_results(model, X, Y, extras[['trip_id']], config)
    predictions.rename(columns={'prediction': config['target_feature']}, inplace=True)
    return geojsonify(extras['segmentgeo'], extras['segment_length'], predictions[config['target_feature']], trip)
    # geos = extras['segmentgeo'].map(geojson.loads).values
    # props = pd.concat([extras['segment_length'], predictions[config['target_feature']]], axis=1).values.T
    # temp = [0 for _ in range(len(props[0]))]
    # for i in range(len(props[0])):
    #     temp[i] = props[1][i] if i == 0 else temp[i - 1] + props[1][i]
    # props = np.vstack([props, temp])
    # for i in range(len(props[0])):
    #     temp[i] = props[0][i] if i == 0 else temp[i - 1] + props[0][i]
    # props = np.vstack([props, temp])
    # other_preds_df = get_baseline_and_actual(trip)
    # geostrings = [geojson.Feature() for _ in range(len(geos))]
    # for i in range(len(geos)):
    #     geostrings[i] = geojson.Feature(geometry=geos[i],
    #                                     properties={'cost': props[1][i],
    #                                                 'agg_cost': props[2][i],
    #                                                 'length': props[0][i],
    #                                                 'agg_length': props[3][i],
    #                                                 'baseline': other_preds_df['baseline'][i],
    #                                                 'agg_baseline': other_preds_df['agg_baseline'][i],
    #                                                 'actual': other_preds_df['actual'][i],
    #                                                 'agg_actual': other_preds_df['agg_actual'][i]})
    # return str(geojson.dumps(geojson.FeatureCollection(geostrings)))


def segmentlist_prediction(route):
    pass


def existing_trips_prediction():
    X, Y, extras = get_candidate_trip_data(known_energy_trips, config, retain_id=True)

    keys = X[['mapmatched_id']]
    X.drop(['mapmatched_id'], axis=1, inplace=True)

    predictions, _, _ = calculate_results(model, X, Y, extras[['trip_id']], config)

    predictions.rename(columns={'0': 'prediction'})
    predictions['id'] = keys['mapmatched_id']
    path = model_path(config) + "/candidate_predictions.csv"
    predictions[['id', 'prediction']].to_csv(path, index=False, header=False)
    print("Predictions saved to file:" + path)

    copy_latest_preds_transaction(path, main_db)

    return "Database updated with trip predictions for model: " + current_model


def load_new_model(path):
    global config, model
    config = load_config(path)
    model = load_model(config)
