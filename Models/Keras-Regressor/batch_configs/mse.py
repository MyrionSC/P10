from Utils import Configuration

batch_name = "MeanSquaredError"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"
configs = []

configMAE = default_config.copy()
configMAE['model_name_base'] = "MSE_NoScale"
configMAE['embedding'] = 'node2vec-64d'
configMAE['features_used'] = ['categoryid', 'segment_length', 'height_change', 'temperature', 'quarter', 'weekday', 'month']
configMAE['loss'] = 'mse'
configMAE['scale'] = False
configs.append(configMAE)

configMAEScale = default_config.copy()
configMAEScale['model_name_base'] = "MSE_Scale"
configMAEScale['embedding'] = 'node2vec-64d'
configMAEScale['features_used'] = ['categoryid', 'segment_length', 'height_change', 'temperature', 'quarter', 'weekday', 'month']
configMAEScale['loss'] = 'mse'
configMAEScale['scale'] = True
configs.append(configMAEScale)
