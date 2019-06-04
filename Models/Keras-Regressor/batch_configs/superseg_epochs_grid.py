from Utils import Configuration

batch_name = "SupersegmentEpochsGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
energy_config['epochs'] = 100
energy_config['iterations'] = 1
energy_config['model_name_base'] = "SS_Energy_Epochs_100"
configs = []

for i in range(energy_config['iterations']):
    conf = energy_config.copy()
    conf['model_name_base'] += "_Iter" + str(i + 1)
    configs.append(conf)
