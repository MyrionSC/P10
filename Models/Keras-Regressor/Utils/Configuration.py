paths = {
    'dataPath': "../data/Data.csv",
    'trainPath': "../data/Training.csv",
    'validationPath': "../data/Test.csv",
    'supersegDataPath': "../data/supersegment-data.csv",
    'supersegTrainPath': "../data/supersegment-training.csv",
    'supersegValidationPath': "../data/supersegment-validation.csv",
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
    'iterations': 3,
    'embedding': "node2vec-64d",
    'batch_size': 8192,
    'epochs': 20,  # When training the BESTEST model possible, use 20 or more epochs
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'tanh',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'speed',
    'features_used': ['categoryid', 'segment_length', 'speedlimit', 'incline', 'temperature',
                      'quarter', 'weekday', 'month'],
    'model_name_base': 'DefaultSpeed-epochs_20',
    'batch_dir': "Default_Speed_Models/",
    'scale': True,
    'cyclic_time': False,
    'loss': 'mse',
    'speed_model_path': None,
    'supersegment': False
})

energy_config = Config()
energy_config.update({
    'iterations': 3,
    'embedding': "node2vec-64d",
    'batch_size': 8192,
    'epochs': 20,  # When training the BESTEST model possible, use 20 or more epochs
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'relu',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'ev_kwh',
    'features_used': ['categoryid', 'segment_length', 'speed_prediction', 'incline', 'temperature',
                      'quarter', 'weekday', 'month'],
    'model_name_base': 'DefaultEnergy-epochs_20',
    'batch_dir': "Default_Energy_Models/",
    'scale': True,
    'cyclic_time': False,
    'loss': 'mae',
    'speed_model_path': 'saved_models/Default_Speed_Models/DefaultSpeed-epochs_20', # should be relative path from Keras, eg: saved_models/Speed_Models/Some_Model
    'supersegment': False
})

#speed_config_superseg = Config()
#speed_config_superseg.update({
#    'embedding': "node2vec-64d",
#    'batch_size': 8192,
#    'epochs': 20,  # When training the BESTEST model possible, use 20 or more epochs
#    'hidden_layers': 6,
#    'cells_per_layer': 1000,
#    'initial_dropout': 0,  # Dropout value for the first layer
#    'dropout': 0,  # Dropout value for all layers after the first layer
#    'activation': 'tanh',
#    'kernel_initializer': 'normal',
#    'optimizer': 'adamax',
#    'target_feature': 'speed',
#    'features_used': ['categoryid', 'segment_length', 'speedlimit', 'incline', 'temperature',
#                      'quarter', 'weekday', 'month'],
#    'model_name_base': 'DefaultSpeed-epochs_20',
#    'batch_dir': "Default_Speed_Models/",
#    'scale': True,
#    'cyclic_time': False,
#    'loss': 'mse',
#    'speed_model_path': None
#})

energy_config_superseg = Config()
energy_config_superseg.update({
    'iterations': 3,
    'embedding': None,
    'batch_size': 8192,
    'epochs': 10,  # When training the BESTEST model possible, use 20 or more epochs
    'hidden_layers': 6,
    'cells_per_layer': 1000,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'relu',
    'kernel_initializer': 'normal',
    'optimizer': 'adamax',
    'target_feature': 'ev_wh',
    'features_used': ['cat_start', 'cat_end', 'cat_speed_difference', 'type', 'segment_length', 'incline',
                      'traffic_lights', 'direction', 'temperature', 'quarter', 'weekday', 'month'],
    'model_name_base': 'DefaultEnergy-epochs_20',
    'batch_dir': "Default_Energy_Models_Superseg/",
    'scale': True,
    'cyclic_time': False,
    'loss': 'mae',
    'supersegment': True
    #'speed_model_path': 'saved_models/Default_Speed_Models/DefaultSpeed-epochs_20' # should be relative path from Keras, eg: saved_models/Speed_Models/Some_Model
})

# Possible features: ['categoryid', 'incline', 'segment_length', 'speed_prediction', 'height_change', 'speed', 'temperature', 'headwind_speed', 'quarter', 'weekday', 'month', 'speedlimit', 'intersection']
