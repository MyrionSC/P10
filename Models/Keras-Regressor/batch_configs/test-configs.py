import Configuration

batch_name = "DirTestBatch"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"

configs = []
for i in range(3, 6):
    config = default_config.copy()
    config['epocs'] = i
    configs.append(config)

