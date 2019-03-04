import Configuration

batch_name = "Speed_Models"
default_config = Configuration.speed_config
default_config['batch_dir'] = batch_name + "/"
configs = []

speedConfig = default_config.copy()
speedConfig['model_name_base'] = "Speed_Model_MAE_"
speedConfig['embedding'] = 'node2vec-64d'
speedConfig['features_used'] = ['categoryid', 'segment_length', 'height_change', 'speedlimit', 'temperature', 'quarter', 'weekday', 'month']
speedConfig['loss'] = 'mae'
speedConfig['scale'] = True

speedConfig2 = speedConfig.copy()
speedConfig2['loss'] = 'mse'
speedConfig2['model_name_base'] = "Speed_Model_MSE_"

configs.append(speedConfig)
configs.append(speedConfig2)
