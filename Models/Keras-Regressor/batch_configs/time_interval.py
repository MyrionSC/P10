from Utils import Configuration

batch_name = "TimeIntervals"
speed_config = Configuration.speed_config
energy_config = Configuration.energy_config
speed_config['batch_dir'] = batch_name + "/"
energy_config['batch_dir'] = batch_name + "/"
configs = []

intervals = ['quarter', 'hour', 'two_hour', 'four_hour', 'six_hour', 'twelve_hour']

for x in intervals:
    config = speed_config.copy()
    speed_name = "Speed-" + x.upper()
    config['model_name_base'] = speed_name
    config['features_used'] = [y for y in config['features_used'] if y != "quarter"] + [x]
    configs.append(config)

    config = energy_config.copy()
    config['model_name_base'] = "Energy-" + x.upper()
    config['features_used'] = [y for y in config['features_used'] if y != "quarter"] + [x]
    config['speed_model_path'] = "saved_models/" + batch_name + "/" + speed_name
    configs.append(config)

print("end")
