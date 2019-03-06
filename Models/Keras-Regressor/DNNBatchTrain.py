#!/usr/bin/env python3
import json
from datetime import datetime
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

    for config in configFile['configs']:
        DNN.train(config)

    # print and save model training runtime
    endtime = datetime.now()
    runtime = endtime - starttime

    training_done_msg = "Done training batch: {0}\nstarttime: {1}\nendtime: {2}\nruntime: {3}\n"\
        .format(batchDir, starttime, endtime, runtime)

    print(training_done_msg)

    with open("saved_models/" + batchDir + "/runtime.txt", "w+") as file:  # creates / overwrites file
        file.write(training_done_msg)

    if os.path.exists("Utils/d-msg"):
        os.system("python Utils/d-msg '{0}'".format(training_done_msg))

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
        sorted_model_names = sorted(batch_metrics.keys())
        # for model_name, model_metrics in batch_metrics.items():
        for model_name in sorted_model_names:
            file.write(model_name)
            for key in headers:
                if type(batch_metrics[model_name][key]) is list:
                    file.write(", " + str(batch_metrics[model_name][key][-1]))
                else:
                    file.write(", " + str(batch_metrics[model_name][key]))
            file.write("\n")


if __name__ == '__main__':
    main()
