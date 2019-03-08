from Utils import Configuration

batch_name = "Default_Speed_Models"
default_config = Configuration.speed_config
default_config['batch_dir'] = batch_name + "/"
configs = []

config = default_config.copy()
config['epochs'] = 20
config['model_name_base'] = "DefaultSpeed-epochs_20"
configs.append(config)

