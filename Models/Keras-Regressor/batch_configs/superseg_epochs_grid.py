from Utils import Configuration

batch_name = "SupersegmentEpochsGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
energy_config['epochs'] = 40
energy_config['model_base_name'] = "SS_Energy_Epochs_40"
configs = [energy_config]
