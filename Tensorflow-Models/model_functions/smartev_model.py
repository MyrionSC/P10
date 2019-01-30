from __future__ import absolute_import, division, print_function

import tensorflow as tf
import utils.metrics as um


class SmartEVModel:
    def __init__(self, config):
        self.config = config

    def model_fn(self, features, labels, mode, params):
        # Input Layer:
        # Extract the input into a dense layer, according to the feature_columns.
        network = tf.feature_column.input_layer(features, params['feature_columns'])

        # Hidden Layer:
        # Iterate over the 'hidden_units' list of layer sizes, default is [20].
        for units in params.get('hidden_units', [20]):
            # Add a hidden layer, densely connected on top of the previous layer.
            network = tf.layers.dense(inputs=network, units=units, activation=tf.nn.relu)

        # Output Layer:
        # Connect a linear output layer on top.
        output_layer = tf.layers.dense(inputs=network, units=1)

        """
        Below are the three phases:
         - Training
         - Testing/Evaluation
         - Predicting
        Each of which will be called in the main method at relevant points.
        """

        # Predicting:
        # Reshape the output layer to a 1-dim Tensor to return predictions
        predictions = tf.squeeze(output_layer, 1)

        if mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(mode, predictions={"ev_kwh": predictions})

        # Calculate loss using mean squared error
        average_loss = tf.losses.mean_squared_error(labels, predictions)

        # Pre-made estimators use the total_loss instead of the average,
        # so report total_loss for compatibility
        batch_size = tf.shape(labels)[0]
        total_loss = tf.to_float(batch_size) * average_loss

        # Training:
        if mode == tf.estimator.ModeKeys.TRAIN:
            optimizer = params.get("optimizer", tf.train.AdamOptimizer)
            optimizer = optimizer(params.get("learning_rate", None))
            train_op = optimizer.minimize(
                loss=average_loss,
                global_step=tf.train.get_global_step())

            return tf.estimator.EstimatorSpec(
                mode=mode, loss=total_loss, train_op=train_op)

        # Testing/Evaluation:
        if mode == tf.estimator.ModeKeys.EVAL:
            # Compute evaluation metrics
            metrics = {
                'accuracy': um.accuracy(labels, predictions),
                'rmse': um.rmse(labels, predictions),
                'mae': um.mae(labels, predictions),
                'mse': um.mse(labels, predictions)
            }
            tf.summary.scalar('accuracy', metrics['accuracy'][1])
            tf.summary.scalar('rmse', metrics['rmse'][1])
            tf.summary.scalar('mae', metrics['mae'][1])
            tf.summary.scalar('mse', metrics['mse'][1])

            return tf.estimator.EstimatorSpec(mode, loss=total_loss, eval_metric_ops=metrics)
