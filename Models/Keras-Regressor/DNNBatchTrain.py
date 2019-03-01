#!/usr/bin/env python3
from datetime import datetime
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

batchDir = configFile['batch_name']
starttime = datetime.now()

print("Trained models output dir: " + batchDir)

print("starttime: " + str(starttime))


for config in configFile['configs']:
    pprint.pprint(config)
    history = DNN.train(config)
    plot_history(history.history, config)
    DNN.predict(config, True)

# print and save model training runtime
endtime = datetime.now()
print("endtime: " + str(endtime))
runtime = endtime - starttime
print("runtime: " + str(runtime))

with open("saved_models/" + batchDir + "/runtime.txt", "w+") as file:  # creates / overwrites file
    file.write("starttime: " + str(starttime) + "\n")
    file.write("endtime: " + str(endtime) + "\n")
    file.write("runtime: " + str(runtime) + "\n")



