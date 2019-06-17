from Utils import Configuration

fts = ['cat_start', 'cat_end', 'cat_speed_difference', 'type', 'traffic_lights', 'direction', 'incline']

batch_name = "NoFeaturesGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
energy_config['features_used'] = [x for x in energy_config['features_used'] if x not in fts]
energy_config['model_name_base'] = "SS_Energy_None_"

configs = [energy_config]