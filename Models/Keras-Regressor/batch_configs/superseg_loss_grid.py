from Utils import Configuration

batch_name = "SupersegmentLossGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
configs = []

loss_functions = ['mae', 'mse', 'mape']

for i in range(energy_config['iterations']):
    for f in loss_functions:
        conf = energy_config.copy()
        conf['loss'] = f
        conf['model_name_base'] = "SS_Energy_" + f.upper() + "_Iter" + str(i+1)
        configs.append(conf)

