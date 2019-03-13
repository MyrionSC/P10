from Utils.ReadData import get_candidate_trip_data
from DNNRegressor import calculate_results
from Utils.Model import model_path, load_model
from Utils.SQL import copy_latest_preds_transaction
from Utils.LocalSettings import main_db
from Utils.Utilities import load_config

known_energy_trips = [116699, 91881, 4537, 76966, 52557, 175355, 103715]

current_model = "saved_models/Default_Energy_Models/DefaultEnergy-epochs_20"
config = load_config(current_model)
model = load_model(config)


def existing_trips_prediction(model, config):
    X, Y, trip_ids = get_candidate_trip_data(known_energy_trips, config, retain_id=True)

    keys = X[['mapmatched_id']]
    X.drop(['mapmatched_id'], axis=1, inplace=True)

    predictions, _, _ = calculate_results(model, X, Y, trip_ids, config)

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
    model = load_model(path)
