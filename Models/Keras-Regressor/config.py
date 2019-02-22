paths = {
    'dataPath': "../data/Data.csv",
    'trainPath': "../data/Training.csv",
    'validationPath': "../data/Test.csv",
    'modelDir': "./saved_models/",
    'scalerDir': "./saved_scaler/",
    'historyDir': "./saved_history/",
    'embeddingDir': "./saved_embeddings/",
    'embeddingFile': "node2vec-64d"
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
    'embeddings_used': 'LINE',
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
    'target_feature': ['speed'],
    'remove_features': ['min_from_midnight', 'ev_wh', 'acceleration', 'deceleration', 'headwind_speed', 'weekday'],
    'feature_order': ['incline', 'segment_length', 'temperature', 'speedlimit', 'quarter', 'categoryid', 'month'],
    'model_name': 'SpeedModel-'
}

energy_config = {
    'embeddings_used': 'LINE',
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
    'target_feature': ['ev_wh'],
    'remove_features': ['min_from_midnight', 'acceleration', 'speed', 'deceleration', 'headwind_speed', 'speedlimit', 'quarter', 'categoryid', 'month', 'weekday'],
    'feature_order': ['incline', 'segment_length', 'speed_prediction', 'temperature'],
    'model_name': 'Model-'
}

speed_config['model_name'] += 'epochs={0},hidden_layers={1},cells_per_layer={2},embeddings={3}'.format(speed_config['epochs'], speed_config['hidden_layers'], speed_config['cells_per_layer'], paths['embeddingFile'])
energy_config['model_name'] += 'epochs={0},hidden_layers={1},cells_per_layer={2},embeddings={3}'.format(energy_config['epochs'], energy_config['hidden_layers'], energy_config['cells_per_layer'], paths['embeddingFile'])
speed_config['scaler_name'] = speed_config['model_name'] + '_Scaler'
energy_config['scaler_name'] = energy_config['model_name'] + '_Scaler'

if speed_predictor:
    config = speed_config
else:
    config = energy_config

def_features = ['batch_size', 'epochs', 'hidden_layers', 'cells_per_layer', 'initial_dropout', 'dropout', 'activation', 'kernel_initializer', 'optimizer', 'target_feature', 'remove_features']