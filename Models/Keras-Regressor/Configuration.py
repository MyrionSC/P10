paths = {
    'dataPath': "../data/Data.csv",
    'trainPath': "../data/Training.csv",
    'validationPath': "../data/Test.csv",
    'modelDir': "./saved_models/",
    'scalerDir': "./saved_scaler/",
    'historyDir': "./saved_history/",
    'embeddingDir': "./saved_embeddings/",
    'speedPredPath': "./speed_predictions/"
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


class Config(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


speed_config = Config()
speed_config.update({
    'embedding': "node2vec-64d",
    'batch_size': 8192,
    'epochs': 10,
    'iterations': 1,
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'softsign',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'speed',
    'features_used': ['categoryid', 'segment_length', 'speedlimit', 'height_change', 'temperature',
                      'quarter', 'weekday', 'month'],
    'model_name_base': 'SpeedModel-',
    'batch_dir': "SpeedModel/",
    'speed_prediction_file': "predictions.csv",
    'scale': True,
    'cyclic_quarter': False,
    'loss': 'mse',
    'speed_config': None
})

energy_config = Config()
energy_config.update({
    'embedding': "node2vec-64d",
    'batch_size': 8192,
    'epochs': 10,
    'iterations': 1,
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'relu',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'ev_kwh',
    'features_used': ['categoryid', 'segment_length', 'speed_prediction', 'height_change', 'temperature',
                      'quarter', 'weekday', 'month'],
    'model_name_base': 'Model-',
    'batch_dir': "TestOutput/",
    'speed_prediction_file': "predictions.csv",
    'scale': True,
    'cyclic_quarter': False,
    'loss': 'mse',
    'speed_config': speed_config
})

# Possible features: ['categoryid', 'incline', 'segment_length', 'speed_prediction', 'height_change', 'speed', 'temperature', 'headwind_speed', 'quarter', 'weekday', 'month', 'speedlimit', 'intersection']


def model_dir_name(config: Config) -> str:
    return config['batch_dir'] + config['model_name_base'] + 'epochs_{0}-hidden_layers_{1}-cells_per_layer_{2}-embeddings_{3}/'.format(config['epochs'], config['hidden_layers'], config['cells_per_layer'], config['embedding'])


def model_path(config: Config) -> str:
    return paths['modelDir'] + model_dir_name(config)

