import os
import tensorflow as tf

from input_functions.iris_input import IrisDataset
from model_functions.iris_model import IrisModel
from utils.config import process_config
from utils.dirs import create_dirs
from utils.utils import get_args


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

    feature_columns = [tf.feature_column.numeric_column(key, shape=1) for key in config.feature_keys]
    model_function = IrisModel(config).model_fn

    model = tf.estimator.Estimator(
        model_fn=model_function,
        params={
            "feature_columns": feature_columns,
            "hidden_units": [20, 20],
            "n_classes": config.n_classes
        })

    eval_result, _ = train_and_evaluate(config, model)
    print("Done!")


def train_and_evaluate(config, estimator):
    train_input_fn = IrisDataset(config, is_training=True).input_fn
    validation_input_fn = IrisDataset(config).input_fn

    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, max_steps=config.num_epochs)
    validation_spec = tf.estimator.EvalSpec(input_fn=validation_input_fn)

    return tf.estimator.train_and_evaluate(estimator, train_spec, validation_spec)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    main()
