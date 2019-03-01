import Configuration

batch_name = "DirTestBatch"
default_config = Configuration.energy_config
default_config['batch_dir'] = batch_name + "/"

confs = [{'features_used': ['incline', 'segment_length', 'categoryid', 'speedlimit', 'intersection']}]
# Generate configurations here and add them to the confs list
configs = []
for i in range(len(confs)):
    configs.append(default_config.copy())
    configs[i].update(confs[i])
