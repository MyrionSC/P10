from Utils import Configuration

batch_name = "SpeedDropout"
default_config = Configuration.speed_config
default_config['batch_dir'] = batch_name + "/"
configs = []

actii = ['relu', 'softsign', 'tanh']
init_dropout = [0.0, 0.25, 0.5]
dropout = [0.0, 0.25, 0.5]

for initial in init_dropout:
    for rest in dropout:
        for act in actii:
            config = default_config.copy()
            config['model_name_base'] = "Speed-" + act.upper() + "-Init_{0:.2f}-Dropout_{1:.2f}".format(initial, rest)
            config['initial_dropout'] = initial
            config['dropout'] = rest
            config['activation'] = act
            configs.append(config)
