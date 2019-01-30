from Utils import plot_history, save_model, read_data
from Model import DNNRegressor
from tensorflow import set_random_seed
from numpy.random import seed
from sklearn.metrics import r2_score
import itertools as it
import time
import json
import os

seed(1337)  # Numpy seed
set_random_seed(1337)  # TensorFlow seed

# Read the data from the specified CSV file
dataPath = "../data/Data.csv"
trainPath = "../data/Training.csv"
validationPath = "../data/Validation.csv"
embTransformed64Path = "../data/osm_dk_20140101-transformed-64d.emb"
embTransformed32Path = "../data/osm_dk_20140101-transformed-32d.emb"
embNormal32Path = "../data/osm_dk_20140101-normal-32d.emb"

# Testing different embedding parameters
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-0.25.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-0.5.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-2.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-4.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-q-0.25.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-q-0.5.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-q-2.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-q-4.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-4-q-0.25.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-0.25-q-4.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-p-0.5-q-2.emb"

# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-walk_length-40.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-walk_length-120.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-walks-5.emb"
# embTransformed32Path = "../data/osm_dk_20140101-transformed-32d-walks-18.emb"

# Graphsage embeddings
# embTransformed32Path = "../data/GraphSAGE_mean_big_0.00001_identity_32-embeddings.csv"
# embTransformed32Path = "../data/graphsage_maxpool_big_0.00001_identity_32-embeddings.csv"

embTransformedPath = ["../data/osm_dk_20140101-transformed-32d.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-0.25.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-0.5.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-2.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-4.emb",
                      "../data/osm_dk_20140101-transformed-32d-q-0.25.emb",
                      "../data/osm_dk_20140101-transformed-32d-q-0.5.emb",
                      "../data/osm_dk_20140101-transformed-32d-q-2.emb",
                      "../data/osm_dk_20140101-transformed-32d-q-4.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-4-q-0.25.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-0.25-q-4.emb",
                      "../data/osm_dk_20140101-transformed-32d-p-0.5-q-2.emb",
                      "../data/osm_dk_20140101-transformed-32d-walk_length-40.emb",
                      "../data/osm_dk_20140101-transformed-32d-walk_length-120.emb",
                      "../data/osm_dk_20140101-transformed-32d-walks-5.emb",
                      "../data/osm_dk_20140101-transformed-32d-walks-5.emb",
                      "../data/osm_dk_20140101-transformed-32d-walks-18.emb",
                      "../data/osm_dk_20140101-transformed-64d.emb",
                      "../data/GraphSAGE_mean_big_0.00001_identity_32-embeddings.csv",
                      "../data/graphsage_maxpool_big_0.00001_identity_32-embeddings.csv"]

# Define training parameters. Supply multiple for grid search
batch_size = [8192]
epochs = [10]
iterations = [1, 2, 3]
hidden_layers = [4]
cells_per_layer = [1000]
initial_dropout = [0]  # Dropout value for the first layer
dropout = [0]  # Dropout value for all layers after the first layer
activation = ['relu']
# activation = ['softmax', 'elu', 'selu', 'softplus', 'softsign', 'relu', 'tanh', 'sigmoid', 'hard_sigmoid', 'exponential']
kernel_initializer = ['normal']
optimizer = ['adam']
# optimizer = ['sgd', 'rmsprop', 'adagrad', 'adadelta', 'adam', 'adamax', 'nadam']

# When predicting speed, these features are always removed: 'min_from_midnight', 'speed', 'acceleration', 'deceleration'
target_feature = ['ev_wh']
remove_features_grid = [['min_from_midnight', 'speed', 'acceleration', 'deceleration'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'categoryid'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'incline'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'segment_length'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'temperature'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'headwind_speed'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'quarter'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'weekday'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'month'],
                        ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'speedlimit']]

# When predicting speed, these features are always removed: 'min_from_midnight', 'ev_wh', 'acceleration', 'deceleration'
# target_feature = ['speed']
# remove_features_grid = [['min_from_midnight', 'ev_wh', 'acceleration', 'deceleration', 'headwind_speed', 'weekday']]

data_param_grid = dict(remove_features=remove_features_grid, embTransformedPath=embTransformedPath)
allDataNames = sorted(data_param_grid)
data_combinations = (dict(zip(allDataNames, dataparams)) for dataparams in it.product(*(data_param_grid[Name] for Name in allDataNames)))

history_collection = list()

for data_params in data_combinations:
    print(data_params['embTransformedPath'] + "  -  Removed features: " + ', '.join(data_params['remove_features']))

    param_grid = dict(batch_size=batch_size, epochs=epochs, hidden_layers=hidden_layers,
                      cells_per_layer=cells_per_layer, activation=activation,
                      kernel_initializer=kernel_initializer, optimizer=optimizer, initial_dropout=initial_dropout,
                      dropout=dropout, iteration=iterations)
    allNames = sorted(param_grid)
    combinations = (dict(zip(allNames, params)) for params in it.product(*(param_grid[Name] for Name in allNames)))

    X_train, Y_train, num_features, num_labels, embeddings_used, trip_ids_train \
        = read_data(trainPath, target_feature, data_params['remove_features'], emb_transformed_path=data_params['embTransformedPath'], scale=True, use_speed_prediction=True)
    X_validation, Y_validation, _, _, _, trip_ids_validation \
        = read_data(validationPath, target_feature, data_params['remove_features'], emb_transformed_path=data_params['embTransformedPath'], scale=True, load_scaler=True, use_speed_prediction=True)

    for params in combinations:
        # Create estimator
        estimator = DNNRegressor(num_features, num_labels, params['hidden_layers'], params['cells_per_layer'],
                                 params['activation'], params['kernel_initializer'], params['optimizer'], params['initial_dropout'], params['dropout'])

        print("Starting training of DNN using parameters: %s" % params)
        start_time = time.time()
        # Train estimator and get training history
        history = estimator.fit(X_train, Y_train, epochs=params['epochs'], validation_data=(X_validation, Y_validation),
                                batch_size=params['batch_size'], verbose=1, shuffle=True)
        end_time = time.time()
        print('Time to complete %s epochs: %s seconds with batch size %s' % (params['epochs'], end_time - start_time, params['batch_size']))

        # Define new parameter dictionary without iterations (this means only one model is saved)
        params_without_iterations = params
        del params_without_iterations['iteration']
        param_string = ','.join("%s=%s" % (key, value) for (key, value) in params_without_iterations.items())
        target_feature_string = ','.join("%s" % x for x in target_feature)
        embeddings_used_string = ""
        if len(embeddings_used) > 0:
            embeddings_used_string = " - " + ','.join("%s" % x for x in embeddings_used)

        # Save estimator
        model_output_path = ("saved_models/DNNRegressor %s%s - %s" % (target_feature_string, embeddings_used_string, param_string))
        save_model(estimator, model_output_path)
        history_collection.append((data_params, params, history.history))
        print()

        prediction = estimator.predict(X_train, batch_size=params['batch_size'], verbose=1)
        val_prediction = estimator.predict(X_validation, batch_size=params['batch_size'], verbose=1)
        train_r2 = r2_score(Y_train, prediction)
        val_r2 = r2_score(Y_validation, val_prediction)
        history.history['train_r2'] = train_r2
        history.history['val_r2'] = val_r2

        # Save history
        history_output_path = ("saved_history/Predicting %s%s - %s.json" % (target_feature_string, embeddings_used_string, param_string))
        if os.path.isdir("saved_history") and os.path.isfile(history_output_path):
            with open(history_output_path) as f:
                history_list = json.load(f)
        else:
            history_list = list()

        history_list.append(history.history)
        history_json = json.dumps(history_list)

        if not os.path.isdir("saved_history"):
            os.makedirs(os.path.dirname(history_output_path))
        with open(history_output_path, "w") as f:
            f.write(history_json)

for dataparams, parameters, results in history_collection:
    print(parameters)
    print(print(dataparams['embTransformedPath'] + "  -  Removed features: " + ', '.join(dataparams['remove_features'])))
    print("Train R2: {:f}".format(results['train_r2']) + "  -  Validation R2: {:f}".format(results['val_r2']))

# Plot training history
#plot_history(history, metrics=['mean_absolute_error', 'mean_squared_error', 'rmse', 'r2'])

# Print results
# print("Validation results:")
# print("MAE: {:f}".format(history.history['val_mean_absolute_error'][-1]))
# print("MSE: {:f}".format(history.history['val_mean_squared_error'][-1]))
# print("RMSE: {:f}".format(history.history['val_rmse'][-1]))
# print("R2: {:f}".format(history.history['val_r2'][-1]))
# print("")
# print("Training results:")
# print("MAE: {:f}".format(history.history['mean_absolute_error'][-1]))
# print("MSE: {:f}".format(history.history['mean_squared_error'][-1]))
# print("RMSE: {:f}".format(history.history['rmse'][-1]))
# print("R2: {:f}".format(history.history['r2'][-1]))
