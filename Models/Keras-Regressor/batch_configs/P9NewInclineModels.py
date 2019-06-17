from Utils import Configuration

batch_name = "P9Models"
speed_config = Configuration.speed_config
energy_config = Configuration.energy_config
speed_config['batch_dir'] = batch_name + "/"
speed_config['model_name_base'] = "SpeedModel"

energy1 = energy_config.copy()
energy1['batch_dir'] = batch_name + "/"
energy1['speed_model_path'] = "saved_models/" + speed_config['batch_dir'] + speed_config['model_name_base']
energy1['model_name_base'] = "WithEmbeddings"

energy2 = energy_config.copy()
energy2['model_name_base'] = "NoEmbeddings"
energy2['features_used'] = energy_config['features_used'][:]
energy2['features_used'].remove("speed_prediction")
energy2['embedding'] = None

configs = [speed_config, energy1, energy2]
