import os
import tensorflow as tf
import tensorflow.feature_column as fc

from input_functions.smartev_input import DataInput
from model_functions.smartev_model import SmartEVModel
from utils.config import process_config
from utils.dirs import create_dirs
from utils.utils import get_args
import utils.dicts as dicts


def main():
    # capture the config path from the run arguments
    # then process the json configuration file
    try:
        args = get_args()
        config = process_config(args.config)
    except Exception as e:
        print("Missing or invalid arguments %s" % e)
        exit(0)

    # create the experiments dirs
    config.model_dir = os.path.join("../experiments", config.exp_name, "model/")
    create_dirs([config.summary_dir, config.checkpoint_dir, config.model_dir])

    # TODO: Any kind of normalization on labels?
    # Get feature columns
    feature_columns = get_feature_columns()

    # Build a custom Estimator, using the model_fn from SmartEVModel
    model = tf.estimator.Estimator(
        model_fn=SmartEVModel(config).model_fn,
        params={
            "feature_columns": feature_columns,
            "learning_rate": config.learning_rate,
            "optimizer": tf.train.AdamOptimizer,
            "hidden_units": [20, 20]
        })

    eval_result, _ = train_and_evaluate(config, model)


def train_and_evaluate(config, estimator):
    train_input_fn = DataInput(config, is_training=True).input_fn
    validation_input_fn = DataInput(config).input_fn

    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn)
    validation_spec = tf.estimator.EvalSpec(input_fn=validation_input_fn)

    return tf.estimator.train_and_evaluate(estimator, train_spec, validation_spec)


def get_feature_columns():
    # TODO: Build support functions for easier creation of feature columns
    segment_length_bound, min_from_midnight_bound, temperature_bound, headwind_speed_bound, incline_bound, combined_speed_bound = [], [], [], [], [], []
    for i in range(0, 10025, 25):
        segment_length_bound.append(i)
    for i in range(0, 1470, 30):
        min_from_midnight_bound.append(i)
    for i in range(-20, 45, 5):
        temperature_bound.append(i)
#    for i in range(-26, 27, 1):
#        headwind_speed_bound.append(i)
    for i in range(-60, 85, 5):
        incline_bound.append(i)
    for i in range(-25, 65, 1):
        combined_speed_bound.append(i)

    categoryid_c = fc.indicator_column(fc.categorical_column_with_vocabulary_list(key="categoryid", dtype=tf.string,
                                                                                  vocabulary_list=dicts.categories.keys()))
    incline_c = fc.bucketized_column(fc.numeric_column(key="incline", dtype=tf.float32),
                                           incline_bound)
    segment_length_c = fc.bucketized_column(fc.numeric_column(key="segment_length", dtype=tf.float32),
                                            segment_length_bound)
    combined_speed_c = fc.bucketized_column(fc.numeric_column(key="combined_speed", dtype=tf.float32),
                                   combined_speed_bound)
    temperature_c = fc.bucketized_column(fc.numeric_column(key="temperature", dtype=tf.float32),
                                             temperature_bound)
#    headwind_speed_c = fc.bucketized_column(fc.numeric_column(key="headwind_speed", dtype=tf.float32),
#                                                headwind_speed_bound)
    min_from_midnight_c = fc.bucketized_column(fc.numeric_column(key="min_from_midnight", dtype=tf.int32),
                                               min_from_midnight_bound)
    weekday_c = fc.indicator_column(fc.categorical_column_with_vocabulary_list(key="weekday", dtype=tf.string,
                                                                               vocabulary_list=dicts.weekdays.keys()))
    month_c = fc.indicator_column(fc.categorical_column_with_vocabulary_list(key="month", dtype=tf.string,
                                                                             vocabulary_list=dicts.months.keys()))

    return [categoryid_c, incline_c, segment_length_c, combined_speed_c, temperature_c,
            min_from_midnight_c, weekday_c, month_c]


if __name__ == '__main__':
    # The Estimator periodically generates "INFO" logs; make these logs visible.
    tf.logging.set_verbosity(tf.logging.INFO)
    main()
