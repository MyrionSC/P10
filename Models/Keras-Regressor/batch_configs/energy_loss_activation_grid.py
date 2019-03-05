import Configuration

batch_name = "ActivationFunctions"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"
configs = []


lossList = ["mse", "mae"]
actiList = ["relu", "tanh", "sigmoid", "softsign"]

for loss in lossList:
    for acti in actiList:
        config = default_config.copy()
        config['model_name_base'] = loss.upper() + "_" + acti.upper()
        config['loss'] = loss
        config['activation'] = acti
        configs.append(config)


# Speed_Models/Speed_Model_MAE_epochs_10-hidden_layers_6-cells_per_layer_1000-embeddings_node2vec-64d
# configSoftSign['speed_model_path'] = "Speed_Models/Speed_Model_MAE_epochs_10-hidden_layers_6-cells_per_layer_1000-embeddings_node2vec-64d"



# Possible features: ['categoryid', 'incline', 'segment_length', 'speed_prediction', 'height_change',
# 'speed', 'temperature', 'headwind_speed', 'quarter', 'weekday', 'month', 'speedlimit', 'intersection']
# energy_config.update({
#     'embedding': "node2vec-64d",
#     'batch_size': 8192,
#     'epochs': 10,
#     'iterations': 1,
#     'hidden_layers': 6,
#     'cells_per_layer': 1000,
#     'initial_dropout': 0,  # Dropout value for the first layer
#     'dropout': 0,  # Dropout value for all layers after the first layer
#     'activation': 'relu',
#     'kernel_initializer': 'normal',
#     'optimizer': 'adamax',
#     'target_feature': 'ev_kwh',
#     'features_used': ['incline', 'segment_length', 'speed_prediction', 'categoryid', 'speedlimit'],
#     'model_name_base': 'Model-',
#     'batch_dir': "TestOutput/",
#     'speed_prediction_file': "predictions.csv",
#     'scale': True,
#     'cyclic_quarter': False
# })

