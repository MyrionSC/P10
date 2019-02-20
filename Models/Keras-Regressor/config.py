paths = {
    'dataPath': "../data/Data.csv",
    'trainPath': "../data/Training.csv",
    'validationPath': "../data/Test.csv",
    'modelDir': "./saved_models/",
    'scalarDir': "./saved_scalar/",
    'historyDir': "./saved_history/",
    'embeddingDir': "./saved_embeddings/"
}

embedding_config = {
    'node2vec': {
        'p': 1,
        'q': 1,
        'dims': 64,
        'walk_length': 20,
        'num_walks': 10,
    },
    'graphSAGE': {
        'aggregator': 'mean',
        'hidden_units': 1024,
        'dims': 32,
        'learning_rate': 0.000001,
    },
    'LINE': {
        'dims': 20,
        'order': 2,
        'negative': 5,
        'samples': 1,
        'learning_rate': 0.025,
    }
}

config = {
    'embeddings_used': None,
    'graph_type': 'transformed',
    'batch_size': 8192,
    'epochs': 1,
    'iterations': 1,
    'hidden_layers': 1,
    'cells_per_layer': 100,
    'initial_dropout': 0,  # Dropout value for the first layer
    'dropout': 0,  # Dropout value for all layers after the first layer
    'activation': 'softmax',
    'kernel_initializer': 'normal',
    'optimizer': 'adam',
    'target_feature': ['ev_wh'],
    'remove_features': ['min_from_midnight', 'speed', 'acceleration', 'deceleration', 'temperature', 'headwind_speed'],
    'feature_order': ['incline', 'segment_length', 'quarter', 'speedlimit', 'categoryid', 'month', 'weekday'],
    'model_name': "TestModel"
}

def_features = ['batch_size', 'epochs', 'hidden_layers', 'cells_per_layer', 'initial_dropout', 'dropout', 'activation', 'kernel_initializer', 'optimizer', 'target_feature', 'remove_features']