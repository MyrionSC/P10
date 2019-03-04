#!/usr/bin/env bash


if [ "$#" -ne 1 ]; then
    echo "Usage: First argument should be a model batch dir in /home/rmp10/P10/Models/Keras-Regressor/saved_models on the server, or 'latest' to get the most recently trained batch"
    exit
fi

P10=rmp10@172.25.11.191


if [ "$1" = "latest" ]; then
    BATCHNAME=$(ssh $P10 'ls /home/rmp10/P10/Models/Keras-Regressor/saved_models -t | head -1')
else
    BATCHNAME="$1"
fi

echo "Getting plots for batch: $BATCHNAME"
MODELBATCHPATH="/home/rmp10/P10/Models/Keras-Regressor/saved_models/$BATCHNAME"
MODELDIRS=$(ssh $P10 "ls $MODELBATCHPATH")

if [ "$MODELDIRS" = "" ]; then
    exit
fi

rm -rf "$BATCHNAME-plots"
mkdir "$BATCHNAME-plots"

for MODEL in $MODELDIRS; do
    if [ "$MODEL" = "runtime.txt" ]; then
        continue
    fi
    MODELDIR="$BATCHNAME-plots/$MODEL-plots"
    echo "copying plots for $MODEL into $MODELDIR"
    rm -rf $MODELDIR
    mkdir $MODELDIR
    scp $P10:$MODELBATCHPATH/$MODEL/plots/* $MODELDIR
done

