import os
import pandas
import tensorflow as tf

path = "data/training"

# Not tested
for file in os.listdir(path):
    csv = pandas.read_csv(f"{path}/{file}").values
    with tf.python_io.TFRecordWriter(f"{path}/{file}.tfrecords") as writer:
        for row in csv:
            features, label = row[:-1], row[-1]
            example = tf.train.Example()
            example.features.feature["features"].float_list.value.extend(features)
            example.features.feature["label"].int64_list.value.append(label)
            writer.write(example.SerializeToString())