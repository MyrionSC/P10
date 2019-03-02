#!/usr/bin/env bash


if [ "$#" -ne 1 ]; then
    echo "Usage: First argument should be a model batch dir in /home/rmp10/P10/Models/Keras-Regressor/saved_models on the server."
fi


P10=rmp10@172.25.11.191
ModelBatchPath="/home/rmp10/P10/Models/Keras-Regressor/saved_models/$1"

Modeldirs=$(ssh $P10 "ls $ModelBatchPath")

if [ "$Modeldirs" = "" ]; then
    exit
fi

rm -rf "$1-plots"
mkdir "$1-plots"

for model in $Modeldirs; do
    if [ "$model" = "runtime.txt" ]; then
        continue
    fi
    modelDir="$1-plots/$model-plots"
    rm -rf $modelDir
    mkdir $modelDir
    scp $P10:$ModelBatchPath/$model/plots/* $modelDir
done

