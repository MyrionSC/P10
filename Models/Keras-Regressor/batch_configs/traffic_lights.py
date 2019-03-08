from Utils import Configuration

batch_name = "TrafficLights"
speed_config = Configuration.speed_config
energy_config = Configuration.energy_config
speed_config['batch_dir'] = batch_name + "/"
energy_config['batch_dir'] = batch_name + "/"
configs = []


config = speed_config.copy()
config['model_name_base'] = "Speed-TrafficLights"
config['features_used'] += ['intersection']
configs.append(config)

config = energy_config.copy()
config['model_name_base'] = "Energy-TrafficLights"
config['features_used'] += ['intersection']
config['speed_model_path'] = "saved_models/" + batch_name + "/Speed-TrafficLights"
configs.append(config)




