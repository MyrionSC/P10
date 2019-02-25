import DNN_Regressor as DNN
import Configuration


default_config = Configuration.energy_config
configs = [default_config]
configs[0]['epochs'] = 1

for config in configs:
    DNN.train(config)
