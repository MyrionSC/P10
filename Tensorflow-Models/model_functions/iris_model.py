from __future__ import absolute_import, division, print_function

import tensorflow as tf
import utils.metrics as um


class IrisModel:
    def __init__(self, config):
        self.config = config

    def model_fn(self, features, labels, mode, params):
        # Input Layer:
        # Use 'input_layer' to apply the feature columns
        network = tf.feature_column.input_layer(features, params['feature_columns'])

        # Hidden Layer:
        # Build hidden layers, sized according to the 'hidden_units' param
        for units in params['hidden_units']:
            network = tf.layers.dense(network, units=units, activation=tf.nn.relu)

        # Output Layer:
        # Compute logits (1 per class)
        logits = tf.layers.dense(network, params['n_classes'], activation=None)

        """
        Below are the three phases:
         - Training
         - Testing/Evaluation
         - Predicting
        Each of which will be called in the main method at relevant points.
        """

        # Predicting:
        # Compute predictions
        predicted_classes = tf.argmax(logits, 1)
        if mode == tf.estimator.ModeKeys.PREDICT:
            predictions = {
                'class_ids': predicted_classes[:, tf.newaxis],
                'probabilities': tf.nn.softmax(logits),
                'logits': logits
            }
            return tf.estimator.EstimatorSpec(mode, predictions=predictions)

        # Compute loss
        loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

        # Training:
        if mode == tf.estimator.ModeKeys.TRAIN:
            optimizer = tf.train.AdagradOptimizer(self.config.learning_rate)
            train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
            return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

        # Compute evaluation metrics
        metrics = {
            'accuracy': um.accuracy(labels, predicted_classes)
        }
        tf.summary.scalar('accuracy', metrics['accuracy'][1])

        # Testing/Evaluation:
        if mode == tf.estimator.ModeKeys.EVAL:
            return tf.estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=metrics)
