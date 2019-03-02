#!/usr/bin/env bash


if [ "$#" -ne 1 ]; then
    echo "Usage: First argument should be a model batch dir in /home/rmp10/P10/Models/Keras-Regressor/saved_models on the server, or 'latest' to get the most recently trained batch"
    exit
fi

P10=rmp10@172.25.11.191


if [ "$1" = "latest" ]; then
    BatchName=$(ssh $P10 'ls /home/rmp10/P10/Models/Keras-Regressor/saved_models -t | head -1')
else
    BatchName="$1"
fi

ModelBatchPath="/home/rmp10/P10/Models/Keras-Regressor/saved_models/$BatchName"
Modeldirs=$(ssh $P10 "ls $ModelBatchPath")

if [ "$Modeldirs" = "" ]; then
    exit
fi

rm -rf "$BatchName-plots"
mkdir "$BatchName-plots"

for model in $Modeldirs; do
    if [ "$model" = "runtime.txt" ]; then
        continue
    fi
    modelDir="$BatchName-plots/$model-plots"
    rm -rf $modelDir
    mkdir $modelDir
    scp $P10:$ModelBatchPath/$model/plots/* $modelDir
done

