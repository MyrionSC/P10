#!/usr/bin/env python3
import json
from datetime import datetime
from pprint import pprint
import sys
import DNNRegressor as DNN
import os
import errno


def main():
    if len(sys.argv) != 2:
        print("First argument must be a batch_config file. Can usually be found in batch_configs dir")
        exit(errno.E2BIG)

    print("Training with configs from batch file: " + sys.argv[1])

    configFile = {}

    if not os.path.exists(sys.argv[1]):
        print("No such configuration found!")
        exit(errno.ENOENT)

    with open(sys.argv[1]) as f:
        exec(f.read(), configFile)

    batchDir = configFile['batch_name']
    starttime = datetime.now()

    print("Trained models output dir: " + batchDir)
    print("starttime: " + str(starttime))

    for config in configFile['configs']:
        DNN.train(config)

    # print and save model training runtime
    endtime = datetime.now()
    print("endtime: " + str(endtime))
    runtime = endtime - starttime
    print("runtime: " + str(runtime))

    with open("saved_models/" + batchDir + "/runtime.txt", "w+") as file:  # creates / overwrites file
        file.write("starttime: " + str(starttime) + "\n")
        file.write("endtime: " + str(endtime) + "\n")
        file.write("runtime: " + str(runtime) + "\n")

    # After batch training is done, grab all metrics and put them into csv file
    compileBatchMetrics("saved_models/" + batchDir)

def compileBatchMetrics(batch_path: str):
    batch_metrics = {}
    # get model dirs in batch
    model_dirs = [os.path.join(batch_path, o) for o in os.listdir(batch_path) if os.path.isdir(os.path.join(batch_path, o))]
    for model_dir in model_dirs:
        model_name = model_dir.split('/')[-1]
        with open(model_dir + "/history.json", "r") as hist_file:
            batch_metrics[model_name] = json.load(hist_file)

    with open(batch_path + "/batch_metrics.csv", "w+") as file:  # creates / overwrites file
        # create header line
        _, value = next(iter(batch_metrics.items()))
        headers = sorted(value.keys())
        file.write("model_name")
        for header in headers:
            file.write(", " + header)
        file.write("\n")

        # write model metrics
        for model_name, model_metrics in batch_metrics.items():
            print()
            print(model_name)
            file.write(model_name)

            for key in headers:
                if type(model_metrics[key]) is list:
                    print(str(model_metrics[key][-1]))
                    file.write(", " + str(model_metrics[key][-1]))
                else:
                    print(str(str(model_metrics[key])))
                    file.write(", " + str(model_metrics[key]))
            file.write("\n")


if __name__ == '__main__':
    main()
