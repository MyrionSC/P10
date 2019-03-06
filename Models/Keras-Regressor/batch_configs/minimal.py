from Utils import Configuration

batch_name = "MinimalModel"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"
configs = []

configScale = default_config.copy()
configScale['model_name_base'] = "Scale"
configScale['embedding'] = None
configScale['features_used'] = ['categoryid', 'segment_length', 'height_change', 'temperature', 'quarter', 'weekday', 'month']
configs.append(configScale)


configNoScale = default_config.copy()
configNoScale['model_name_base'] = "NoScale"
configNoScale['embedding'] = None
configNoScale['features_used'] = ['categoryid', 'segment_length', 'height_change', 'temperature', 'quarter', 'weekday', 'month']
configNoScale['scale'] = True
configs.append(configNoScale)


# Possible features: ['categoryid', 'incline', 'segment_length', 'height_change',
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
