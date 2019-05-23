from Utils import Configuration

batch_name = "SupersegmentLayersUnitsGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
configs = []

num_layers = [2, 3, 4, 5, 6]
num_units = [500, 1000, 1500, 2000]

for nl in num_layers:
    for nu in num_units:
        conf = energy_config.copy()
        conf['hidden_layers'] = nl
        conf['cells_per_layer'] = nu
        conf['model_name_base'] = "SS_Energy_" + str(nl) + "Layers_" + str(nu) + "Units"
        configs.append(conf)
