import tensorflow as tf
from utils import utils


# A wrapper class for the input function to the custom estimator
# The input function tells Tensorflow how to read and organize the data, and has 3 main tasks:
#   1: Read the data from the csv file
#   2: Determine what data is training and what data is validation
#   3: Determine which columns are features and which columns are labels
class DataInput:
    """
    Smart Ev Dataset - load data from the disk
    """

    # The wrapper is simply an object to contain the configuration parameters for Tensorflow
    def __init__(self, config, is_training=False):
        self.config = config
        self.is_training = is_training

        # if self.is_training:
        #    self.file_name = config.train_file
        # else:
        #    self.file_name = config.test_file

    # The actual input function to be passed to the estimator specifications
    def input_fn(self):
        # Reads the csv file specified in the config into a Tensorflow Dataset object
        dataset = tf.contrib.data.CsvDataset(self.config.train_file,
                                             utils.string_array_to_dtypes(self.config.feature_types,
                                                                          self.config.record_defaults),
                                             header=True)
        # Skip the csv header
        dataset = dataset.skip(1)

        # Spilt the data into a 70/30 split between training and validation data
        # The validation data is the first 3 records (the data is roughly 10 million lines)
        # The test data is the remaining around 7 million records.
        if self.is_training:
            dataset = dataset.skip(3000000)
            # Shuffle and repeat the dataset to return a new permutation for each epoch
            dataset = dataset.apply(
                tf.contrib.data.shuffle_and_repeat(32 * self.config.batch_size, self.config.no_epochs))
        else:
            dataset = dataset.take(3000000)
            dataset = dataset.shuffle(32 * self.config.batch_size)

        # Split the data into batches
        dataset = dataset.batch(batch_size=self.config.batch_size)

        # Prefetch batch
        # Since batch is used before prefetch, the number of elements is batch_size * prefetch_buffer_size
        #dataset = dataset.prefetch(buffer_size=self.config.prefect_buffer_size)

        # Get a one-shot iterator for the data set
        iterator = dataset.make_one_shot_iterator()

        # Map the configs feature keys to the actual columns of the dataset
        columns = iterator.get_next()
        features = {}
        for index, key in enumerate(self.config.feature_keys):
            features[key] = columns[index]

        # Determine the label as simply the final column of the dataset
        label = columns[-1]

        return features, label
