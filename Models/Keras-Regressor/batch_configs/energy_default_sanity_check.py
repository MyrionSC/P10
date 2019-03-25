from Utils import Configuration

batch_name = "DefaultEnergySanityCheck"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"
configs = []

for num in range(1,6):
    config = default_config.copy()
    config['model_name_base'] = "Num_" + str(num)
    configs.append(config)
