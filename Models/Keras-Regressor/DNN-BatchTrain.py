import DNN_Regressor as DNN
import Configuration


def generate_configs():
    batch_name = "TestBatch1"
    default_config = Configuration.energy_config
    default_config['batch_dir'] = batch_name + "/"

    confs = [{'epochs': 10}]
    # Generate configurations here and add them to the confs list
    new_confs = []
    for i in range(len(confs)):
        new_confs.append(default_config.copy())
        new_confs[i].update(confs[i])

    return new_confs


configs = generate_configs()

for config in configs:
    DNN.train(config)
