from Utils import Configuration

batch_name = "PlotTest2"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"


config = default_config.copy()
config['epochs'] = 10
config['hidden_layers'] = 1
config['cells_per_layer'] = 100
config['features_used'] = ['categoryid']

configs = [config]


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


# for i in range(1, 2):
#     config = default_config.copy()
#     config['epochs'] = i
#     configs.append(config)

