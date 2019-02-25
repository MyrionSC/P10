paths = {
    'dataPath': "../data/Data.csv",
    'trainPath': "../data/Training.csv",
    'validationPath': "../data/Test.csv",
    'modelDir': "./saved_models/",
    'scalerDir': "./saved_scaler/",
    'historyDir': "./saved_history/",
    'embeddingDir': "./saved_embeddings/",
    'speedPredPath': "../data/"
}

embedding_config = {
    'node2vec': {
        'p': 1,
        'q': 1,
        'dims': 64,
        'walk_length': 20,
        'num_walks': 10,
    },
    'graphSAGE': {
        'aggregator': 'mean',
        'hidden_units': 1024,
        'dims': 32,
        'learning_rate': 0.000001,
    },
    'LINE': {
        'dims': 20,
        'order': 2,
        'negative': 5,
        'samples': 1,
        'learning_rate': 0.025,
    }
}

speed_predictor = False

speed_config = {
    'embedding': "node2vec-64d",
    'batch_size': 8192,
    'epochs': 20,
    'iterations': 1,
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'softsign',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'speed',
    'remove_features': ['min_from_midnight', 'ev_wh', 'acceleration', 'deceleration', 'headwind_speed', 'weekday'],
    'feature_order': ['incline', 'segment_length', 'temperature', 'speedlimit', 'quarter', 'categoryid', 'month'],
    'model_name': 'SpeedModel-',
    'batch_dir': "TestOutput"
}

energy_config = {
    'embedding': "node2vec-64d",
    'speed_predictions_file': "speed_prediction.csv",
    'batch_size': 8192,
    'epochs': 20,
    'iterations': 1,
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'relu',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'ev_wh',
    'remove_features': ['min_from_midnight', 'acceleration', 'speed', 'deceleration', 'headwind_speed', 'speedlimit', 'quarter', 'categoryid', 'month', 'weekday'],
    'feature_order': ['incline', 'segment_length', 'speed_prediction', 'temperature'],
    'model_name_base': 'Model-',
    'batch_dir': "TestOutput"
}


def model_name(config):
    return config('model_name_base') + 'epochs={0},hidden_layers={1},cells_per_layer={2},embeddings={3}'.format(config['epochs'], config['hidden_layers'], config['cells_per_layer'], config['embedding'])


def scaler_name(config):
    return model_name(config) + '_Scaler'
