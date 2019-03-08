from Utils import Configuration

batch_name = "LINEModels"
speed_config = Configuration.speed_config
speed_config['batch_dir'] = batch_name + "/"
energy_config = Configuration.energy_config
energy_config['batch_dir'] = batch_name + "/"
configs = []

config = speed_config.copy()
config['model_name_base'] = "Speed-LINE-64d"
config['embedding'] = "LINE-64d"
configs.append(config)

config = energy_config.copy()
config['model_name_base'] = "Energy-LINE-64d"
config['embedding'] = "LINE-64d"
configs.append(config)


