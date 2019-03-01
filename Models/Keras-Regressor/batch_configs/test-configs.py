import Configuration

batch_name = "DirTestBatch"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"

configs = []
for i in range(1, 3):
    config = default_config.copy()
    config['epochs'] = i
    configs.append(config)

