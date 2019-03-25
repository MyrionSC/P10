from Utils import Configuration

batch_name = "Energy_More_Resources"
default_config = Configuration.speed_config
default_config['batch_dir'] = batch_name + "/"
configs = []

config = default_config.copy()
config['epochs'] = 30
config['model_name_base'] = "30-epochs"
configs.append(config)

config2 = default_config.copy()
config2['epochs'] = 30
config2['hidden_layers'] = 8
config2['cells_per_layer'] = 1500
config2['model_name_base'] = "30-epochs_8-layers_1500-cells"
configs.append(config2)

