#!/usr/bin/env python3
import sys
import os
import json
from Utils.Model import model_path
from DNNSegmentPredictor import create_segment_predictions
from Utils.LocalSettings import local_db
from Utils.SQL import index_qry, copy_qry, table_qry, write_transaction


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) != 2:
        print("Invalid number of arguments: " + str(len(args)))
        print("Expected 2")
        quit()

    modelpath = args[0].strip()
    if not os.path.isdir(modelpath):
        print("Specified model does not exist")
        quit()

    tablename = args[1].strip()

    print("Loading model configuration")
    with open(modelpath + "config.json", "r") as f:
        config = json.load(f)
    if not os.path.isfile(model_path(config) + "segment_predictions.csv"):
        print("No predictions present: Generating")
        create_segment_predictions(config)

    qrys = [
        table_qry(tablename),
        copy_qry(tablename, os.path.abspath(model_path(config))),
        index_qry(tablename)
    ]

    write_transaction(qrys, local_db)
