from Utils import Configuration

batch_name = "MeanAbsoluteError"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"
configs = []

configMAE = default_config.copy()
configMAE['model_name_base'] = "MAE"
configMAE['embedding'] = 'node2vec-64d'
configMAE['features_used'] = ['categoryid', 'segment_length', 'height_change', 'temperature', 'quarter', 'weekday', 'month']
configMAE['loss'] = 'mae'
configMAE['scale'] = False
configs.append(configMAE)

configMAEScale = default_config.copy()
configMAEScale['model_name_base'] = "MAE_Scale"
configMAEScale['embedding'] = 'node2vec-64d'
configMAEScale['features_used'] = ['categoryid', 'segment_length', 'height_change', 'temperature', 'quarter', 'weekday', 'month']
configMAEScale['loss'] = 'mae'
configMAEScale['scale'] = True
configs.append(configMAEScale)
