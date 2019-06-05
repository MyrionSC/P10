from Utils.Configuration import energy_config_superseg

config = energy_config_superseg.copy()
config['batch_dir'] = "FinalSupersegModel"
config['model_name_base'] = "FinalSupersegModel"
config['epochs'] = 25
config['loss'] = 'mse'
config['cells_per_layer'] = 1000
config['hidden_layers'] = 6

configs = []
for i in range(config['iterations']):
    conf = config.copy()
    conf['model_name_base'] += "_Iter" + str(i + 1)
    configs.append(conf)