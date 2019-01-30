import tensorflow as tf
import tensorflow.metrics as tfm


def accuracy(labels, predictions):
    return tfm.accuracy(labels=labels, predictions=predictions, name='accuracy_op')


def rmse(labels, predictions):
    return tfm.root_mean_squared_error(labels=labels, predictions=predictions, name='rmse_op')


def mae(labels, predictions):
    return tfm.mean_absolute_error(labels=labels, predictions=predictions, name='mae_op')


def mse(labels, predictions):
    return tfm.mean_squared_error(labels=labels, predictions=predictions, name='mse_op')
