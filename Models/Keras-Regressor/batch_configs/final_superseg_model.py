from Utils.Configuration import energy_config_superseg

batch_name = "FinalSupersegModel"
config = energy_config_superseg
config['batch_dir'] = batch_name + "/"
config['model_name_base'] = "FinalSupersegModel"
config['epochs'] = 25
config['loss'] = 'mae'
config['cells_per_layer'] = 1000
config['hidden_layers'] = 6

configs = []
for i in range(config['iterations']):
    conf = config.copy()
    conf['model_name_base'] += "_Iter" + str(i + 1)
    configs.append(conf)