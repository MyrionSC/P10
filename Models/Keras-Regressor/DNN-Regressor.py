from Utils import save_model, read_data, embedding_path
from Model import DNNRegressor
from config import paths, config, def_features, speed_predictor
from tensorflow import set_random_seed
from numpy.random import seed
from sklearn.metrics import r2_score
import time
import json
import os

seed(1337)  # Numpy seed
set_random_seed(1337)  # TensorFlow seed


def read_data_sets():
    print("")
    print("------ Reading training data ------")
    start_time = time.time()
    X_train, Y_train = read_data(paths['trainPath'], scale=True, re_scale=True,
                                                           use_speed_prediction=not speed_predictor)
    print("Training data read")
    print("Time elapsed: %s" % (time.time() - start_time))

    print("")
    print("------ Reading validation data ------")
    start_time = time.time()
    X_validation, Y_validation = read_data(paths['validationPath'], scale=True,
                                                 use_speed_prediction=not speed_predictor)
    print("Validation data read")
    print("Time elapsed: %s seconds" % (time.time() - start_time))

    return X_train, Y_train, X_validation, Y_validation


def train_model(X_train, Y_train, X_validation, Y_validation):
    print("")
    print("------ Training -----")
    start_time = time.time()

    # Create estimator
    estimator = DNNRegressor(len(list(X_train)), len(list(Y_train)), config['hidden_layers'], config['cells_per_layer'],
                             config['activation'], config['kernel_initializer'], config['optimizer'],
                             config['initial_dropout'], config['dropout'])

    # Train estimator and get training history
    history = estimator.fit(X_train, Y_train, epochs=config['epochs'], validation_data=(X_validation, Y_validation),
                            batch_size=config['batch_size'], verbose=1, shuffle=True)
    save_model(estimator, paths['modelDir'] + config['model_name'])

    print("Model trained for %s epochs" % (config['epochs']))
    print("Time elapsed: %s seconds" % (time.time() - start_time))
    return estimator, history


def calculate_results(estimator, history, X_train, Y_train, X_validation, Y_validation):
    print("")
    print("------ Calculating R2-score ------")
    start_time = time.time()
    prediction = estimator.predict(X_train, batch_size=config['batch_size'], verbose=1)
    val_prediction = estimator.predict(X_validation, batch_size=config['batch_size'], verbose=1)
    train_r2 = r2_score(Y_train, prediction)
    val_r2 = r2_score(Y_validation, val_prediction)
    print("")
    print("Train R2: {:f}".format(train_r2) + "  -  Validation R2: {:f}".format(val_r2))
    print("Time elapsed: %s seconds" % (time.time() - start_time))

    print("")
    print("------ Saving history ------")
    start_time = time.time()
    history.history['train_r2'] = train_r2
    history.history['val_r2'] = val_r2
    if not os.path.isdir(paths['historyDir']):
        os.makedirs(paths['historyDir'])
    with open(paths['historyDir'] + config['model_name'] + '_History.json', "w") as f:
        f.write(json.dumps(config, indent=4))
        f.write(json.dumps(history.history, indent=4))
    print("History saved")
    print("Time elapsed: %s seconds" % (time.time() - start_time))


if __name__ == "__main__":
    X_train, Y_train, X_validation, Y_validation = read_data_sets()
    model, history = train_model(X_train, Y_train, X_validation, Y_validation)
    calculate_results(model, history, X_train, Y_train, X_validation, Y_validation)
