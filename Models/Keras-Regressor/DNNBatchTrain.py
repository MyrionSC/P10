import pprint
import sys
import DNNRegressor as DNN
from Plots import plot_history


if len(sys.argv) != 2:
    print("First argument must be a batch_config file. Can usually be found in batch_configs dir")
    exit()

print("Training with configs from batch file: " + sys.argv[1])

configFile = {}
exec(open(sys.argv[1]).read(), configFile)

for config in configFile['configs']:
    # pprint.pprint(config)
    history = DNN.train(config)
    plot_history(history.history, config)
    DNN.predict(config, True)
