import argparse
import tensorflow as tf


def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-c', '--config',
        metavar='C',
        default='None',
        help='The Configuration file')
    args = argparser.parse_args()
    return args


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
