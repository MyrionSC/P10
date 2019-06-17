from Utils import Configuration

batch_name = "DefaultEnergyNewEv"
speed_config = Configuration.speed_config
energy_config = Configuration.energy_config
speed_config['batch_dir'] = batch_name + "/"
energy_config['batch_dir'] = batch_name + "/"
energy_config['model_name_base'] = "BestModel"
energy_config['speed_model_path'] = "saved_models/" + batch_name + "/" + speed_config['model_name_base']
configs = [energy_config]
