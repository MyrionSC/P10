from Utils import Configuration

batch_name = "DefaultSupersegmentEv"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
configs = [energy_config]
