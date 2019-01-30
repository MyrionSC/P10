import tensorflow as tf
from utils import utils


class BaseDataset:
    def __init__(self, config):
        self.config = config

    def TFRecordDataset(self, file_pattern="", file_path="", is_training=False):
        def _parse_function(example):
            keys_to_features = self.get_keys_to_tfrecord_features_dict(cfg)
            parsed_features = tf.parse_single_example(example, keys_to_features)
            return parsed_features[:(len(keys_to_features) - 1)], parsed_features[-1]

        cfg = self.config
        if cfg.multiple_files:
            # Get all the file with that file pattern and maybe shuffle them
            # Returns a Tensorflow Dataset
            if is_training:
                files = tf.data.Dataset.list_files(file_pattern, cfg.shuffle_files)
            else:
                # Don't shuffle the files if we aren't training
                files = tf.data.Dataset.list_files(file_pattern, shuffle=False)

            # TODO: Should we use compression?
            dataset = files.apply(tf.contrib.data.parallel_interleave(
                lambda filename: tf.data.TFRecordDataset(filename, cfg.compression), cycle_length=4))
        else:
            dataset = tf.data.TFRecordDataset([file_path], cfg.compression,
                                              num_parallel_reads=cfg.TFRecord_num_parallel_reads)

        if is_training:
            dataset = self.repeat(cfg, dataset)

        dataset = dataset.apply(tf.contrib.data.map_and_batch(_parse_function, cfg.batch_size, num_parallel_batches=12))
        # Buffer size is prefetch_buffer_size * batch_size elements, since we use .batch before prefetch
        dataset = dataset.prefetch(buffer_size=cfg.prefetch_buffer_size)

        iterator = dataset.make_one_shot_iterator()
        next_element = iterator.get_next()

        return self.get_features_and_label(cfg, next_element)

    @staticmethod
    def repeat(cfg, dataset):
        # Each of the below methods should give enough randomness
        if not cfg.shuffle_files:
            # Since we don't shuffle the files, we will instead shuffle each epoch
            dataset = dataset.apply(tf.contrib.data.shuffle_and_repeat(32 * cfg.batch_size, cfg.no_epochs))
        else:
            # Use .cache to cache the data of the first epoch in RAM since we don't shuffle it for each epoch,
            # but shuffled the files beforehand
            dataset = dataset.cache()
            dataset = dataset.repeat(cfg.no_epochs)
        return dataset

    @staticmethod
    def get_keys_to_tfrecord_features_dict(cfg):
        keys_to_features = {}
        for index in range(len(cfg.keys_to_features.keys)):
            key = cfg.keys_to_features.keys[index]
            dtype = utils.get_tf_dtype_from_string(cfg.keys_to_features.types[index])
            shape = cfg.keys_to_features.shape[index]
            default_value = cfg.keys_to_features.default_value[index]

            keys_to_features[key] = tf.FixedLenFeature(shape=shape, dtype=dtype, default_value=default_value)

        return keys_to_features

    @staticmethod
    def get_features_and_label(cfg, next_element):
        features = {}
        for index, key in enumerate(cfg.keys_to_features.keys):
            features[key] = next_element[index]
        label = next_element[-1]

        return features, label
