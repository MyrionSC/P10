import tensorflow as tf
from utils import utils


class IrisDataset:
    """
    Iris Dataset - load data from the disk
    """

    def __init__(self, config, is_training=False):
        self.config = config
        self.is_training = is_training

        if self.is_training:
            self.file_name = config.train_file
        else:
            self.file_name = config.test_file

    def input_fn(self):
        dataset = tf.contrib.data.CsvDataset(self.file_name,
                                             utils.get_tf_dtypes_from_string_array(self.config.feature_types,
                                                                                   self.config.record_defaults),
                                             header=True)
        dataset = dataset.skip(1)

        if self.is_training:
            dataset = dataset.apply(tf.contrib.data.shuffle_and_repeat(32 * self.config.batch_size))

        # Batch the examples
        dataset = dataset.batch(batch_size=self.config.batch_size)

        # Prefetch batch
        dataset = dataset.prefetch(buffer_size=self.config.batch_size)

        iterator = dataset.make_one_shot_iterator()
        columns = iterator.get_next()
        features = {}
        for index, key in enumerate(self.config.feature_keys):
            features[key] = columns[index]

        return features, columns[-1]
