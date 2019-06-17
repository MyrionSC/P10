from Utils import Configuration

batch_name = "DefaultEnergyNewEv"
#speed_config = Configuration.speed_config
energy_config = Configuration.energy_config
#speed_config['batch_dir'] = batch_name + "/"
energy_config['batch_dir'] = batch_name + "/"
energy_config['features_used'].remove("speed_prediction")
energy_config['embedding'] = None
configs = [energy_config]
