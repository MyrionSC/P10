from Utils import Configuration

batch_name = "SpeedActivationLossGrid"
default_speed_config = Configuration.speed_config
default_speed_config['batch_dir'] = batch_name + "/"
configs = []

# MSE
config_MSE_RELU = default_speed_config.copy()
config_MSE_RELU['model_name_base'] = "MSE_RELU"
config_MSE_RELU['activation'] = 'relu'
config_MSE_RELU['loss'] = 'mse'
configs.append(config_MSE_RELU)

config_MSE_TanH = default_speed_config.copy()
config_MSE_TanH['model_name_base'] = "MSE_TanH"
config_MSE_TanH['activation'] = 'tanh'
config_MSE_TanH['loss'] = 'mse'
configs.append(config_MSE_TanH)

config_MSE_Sigmoid = default_speed_config.copy()
config_MSE_Sigmoid['model_name_base'] = "MSE_Sigmoid"
config_MSE_Sigmoid['activation'] = 'sigmoid'
config_MSE_Sigmoid['loss'] = 'mse'
configs.append(config_MSE_Sigmoid)

config_MSE_SoftSign = default_speed_config.copy()
config_MSE_SoftSign['model_name_base'] = "MSE_SoftSign"
config_MSE_SoftSign['activation'] = 'softsign'
config_MSE_SoftSign['loss'] = 'mse'
configs.append(config_MSE_SoftSign)

#MAE
config_MAE_RELU = default_speed_config.copy()
config_MAE_RELU['model_name_base'] = "MAE_RELU"
config_MAE_RELU['activation'] = 'relu'
config_MAE_RELU['loss'] = 'mae'
configs.append(config_MAE_RELU)

config_MAE_TanH = default_speed_config.copy()
config_MAE_TanH['model_name_base'] = "MAE_TanH"
config_MAE_TanH['activation'] = 'tanh'
config_MAE_TanH['loss'] = 'mae'
configs.append(config_MAE_TanH)

config_MAE_Sigmoid = default_speed_config.copy()
config_MAE_Sigmoid['model_name_base'] = "MAE_Sigmoid"
config_MAE_Sigmoid['activation'] = 'sigmoid'
config_MAE_Sigmoid['loss'] = 'mae'
configs.append(config_MAE_Sigmoid)

config_MAE_SoftSign = default_speed_config.copy()
config_MAE_SoftSign['model_name_base'] = "MAE_SoftSign"
config_MAE_SoftSign['activation'] = 'softsign'
config_MAE_SoftSign['loss'] = 'mae'
configs.append(config_MAE_SoftSign)



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

