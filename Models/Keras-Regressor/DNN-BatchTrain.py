import DNN_Regressor as DNN
import Configuration
from Configuration import Config
from typing import List


def generate_configs() -> List[Config]:
    batch_name = "SpeedModel"
    default_config = Configuration.speed_config
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
    #history = DNN.train(config)
    #plot_history(history.history, config)
    DNN.predict(config, True)
