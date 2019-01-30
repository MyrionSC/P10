import tensorflow as tf
import tensorflow.feature_column as fc


def main():
    feature_columns = get_feature_columns()

    estimator = tf.estimator.DNNRegressor(
        feature_columns=feature_columns,
        hidden_units=[20, 20],
        optimizer=lambda: tf.train.AdamOptimizer(
            learning_rate=tf.train.exponential_decay(
                learning_rate=0.1,
                global_step=tf.train.get_global_step(),
                decay_steps=10000,
                decay_rate=0.96
            )
        )
    )

    estimator.train(train_in)
    metrics = estimator.evaluate(eval_in)

def get_feature_columns():
    # TODO: Build support functions for easier creation of feature columns
    meters_segment_bound, min_from_midnight_bound, air_temperature_bound, tailwind_magnitude_bound, incline_angle_bound = [], [], [], [], []
    for i in range(0, 10025, 25):
        meters_segment_bound.append(i)
    for i in range(0, 1470, 30):
        min_from_midnight_bound.append(i)
    for i in range(-20, 45, 5):
        air_temperature_bound.append(i)
    for i in range(-26, 27, 1):
        tailwind_magnitude_bound.append(i)
    for i in range(-60, 85, 5):
        incline_angle_bound.append(i)

    meters_segment_c = fc.bucketized_column(fc.numeric_column(key="meters_segment", dtype=tf.float32),
                                            meters_segment_bound)
    air_temperature_c = fc.bucketized_column(fc.numeric_column(key="air_temperature", dtype=tf.float32),
                                             air_temperature_bound)
    tailwind_magnitude_c = fc.bucketized_column(fc.numeric_column(key="tailwind_magnitude", dtype=tf.float32),
                                                tailwind_magnitude_bound)
    incline_angle_c = fc.bucketized_column(fc.numeric_column(key="incline_angle", dtype=tf.float32),
                                           incline_angle_bound)
    categoryid_c = fc.indicator_column(fc.categorical_column_with_vocabulary_list(key="categoryid", dtype=tf.string, vocabulary_list=categories.keys()))
    month_c = fc.numeric_column(key="month", dtype=tf.int32)
    weekday_c = fc.indicator_column(fc.categorical_column_with_vocabulary_list(key="weekday", dtype=tf.string, vocabulary_list=weekdays.keys()))
    min_from_midnight_c = fc.bucketized_column(fc.numeric_column(key="min_from_midnight", dtype=tf.int32),
                                               min_from_midnight_bound)

    return [meters_segment_c, categoryid_c, month_c, weekday_c, min_from_midnight_c,
            air_temperature_c, tailwind_magnitude_c, incline_angle_c]


def train_in():
    return input_fn(True)


def eval_in():
    return input_fn(False)


def input_fn(is_training):
    # Reads the csv file specified in the config into a Tensorflow Dataset object
    dataset = tf.contrib.data.CsvDataset("../data/Data3.csv",
                                         string_array_to_dtypes(["float32", "string", "int32", "string", "int32", "float32", "float32", "float32", "float32"],
                                                                [None, None, None, None, None, None, 0.0, 0.0, None]),
                                         header=True)
    # Skip the csv header
    dataset = dataset.skip(1)

    # Spilt the data into a 70/30 split between training and validation data
    # The validation data is the first 3 records (the data is roughly 10 million lines)
    # The test data is the remaining around 7 million records.
    if is_training:
        dataset = dataset.skip(3000000)
        # Shuffle and repeat the dataset to return a new permutation for each epoch
        dataset = dataset.apply(
            tf.contrib.data.shuffle_and_repeat(32 * 256, 10))
    else:
        dataset = dataset.take(3000000)
        dataset = dataset.shuffle(32 * 256)

    # Split the data into batches
    dataset = dataset.batch(batch_size=256)

    # Prefetch batch
    # Since batch is used before prefetch, the number of elements is batch_size * prefetch_buffer_size
    #dataset = dataset.prefetch(buffer_size=self.config.prefect_buffer_size)

    # Get a one-shot iterator for the data set
    iterator = dataset.make_one_shot_iterator()

    # Map the configs feature keys to the actual columns of the dataset
    columns = iterator.get_next()
    features = {}
    for index, key in enumerate(["meters_segment", "categoryid", "month", "weekday", "min_from_midnight", "air_temperature", "tailwind_magnitude", "incline_angle"]):
        features[key] = columns[index]

    # Determine the label as simply the final column of the dataset
    label = columns[-1]

    return features, label

def string_array_to_dtypes(string_array, record_defaults):
    tf_dtypes = []
    for index, type_string in enumerate(string_array):
        if record_defaults[index] is None:
            tf_dtypes.append(string_to_dtype(type_string))
        else:
            tf_dtypes.append(tf.constant([record_defaults[index]], dtype=string_to_dtype(type_string)))
    return tf_dtypes


def string_to_dtype(dtype_string):
    if dtype_string == "int8":
        return tf.int8
    elif dtype_string == "int16":
        return tf.int16
    elif dtype_string == "int32":
        return tf.int32
    elif dtype_string == "int64":
        return tf.int64
    elif dtype_string == "float16":
        return tf.float16
    elif dtype_string == "float32":
        return tf.float32
    elif dtype_string == "float64":
        return tf.float64
    elif dtype_string == "bfloat16":
        return tf.bfloat16
    elif dtype_string == "complex64":
        return tf.complex64
    elif dtype_string == "complex128":
        return tf.complex128
    elif dtype_string == "uint8":
        return tf.uint8
    elif dtype_string == "uint16":
        return tf.uint16
    elif dtype_string == "uint32":
        return tf.uint32
    elif dtype_string == "uint64":
        return tf.uint64
    elif dtype_string == "qint8":
        return tf.qint8
    elif dtype_string == "qint16":
        return tf.qint16
    elif dtype_string == "qint32":
        return tf.qint32
    elif dtype_string == "quint8":
        return tf.quint8
    elif dtype_string == "quint16":
        return tf.quint16
    elif dtype_string == "bool":
        return tf.bool
    elif dtype_string == "string":
        return tf.string
    else:
        return tf.float32


categories = {'1': 'ferry',
              '10': 'motorway',
              '11': 'motorway_link',
              '15': 'trunk',
              '16': 'trunk_link',
              '20': 'primary',
              '21': 'primary_link',
              '25': 'secondary',
              '26': 'secondary_link',
              '30': 'tertiary',
              '31': 'tertiary_link',
              '35': 'unclassified',
              '40': 'residential',
              '45': 'living_street',
              '50': 'service',
              '55': 'road',
              '60': 'track',
              '65': 'unpaved'}

weekdays = {'0': 'monday',
            '1': 'tuesday',
            '2': 'wednesday',
            '3': 'thursday',
            '4': 'friday',
            '5': 'saturday',
            '6': 'sunday'}

if __name__ == '__main__':
    main()
