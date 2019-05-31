from Utils import Configuration

batch_name = "SupersegmentInclineGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
energy_config['hidden_layers'] = 2
energy_config['cells_per_layer'] = 500
energy_config['features_used'].remove("incline")
configs = []

for i in range(energy_config['iterations']):
    conf = energy_config.copy()
    conf['features_used'] = conf['features_used'][:] + ["incline"]
    conf['model_name_base'] = "SS_Energy_Incline_Iter" + str(i + 1)
    configs.append(conf)
    conf = energy_config.copy()
    conf['model_name_base'] = "SS_Energy_NoIncline_Iter" + str(i + 1)
    configs.append(conf)
