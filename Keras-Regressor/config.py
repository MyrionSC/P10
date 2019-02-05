paths = {
    'dataPath': "../data/Data.csv",
    'trainPath': "../data/Training.csv",
    'validationPath': "../data/Test.csv",
    'embTransformed64Path': "../data/osm_dk_20140101-transformed-64d.emb",
    'embTransformed32Path': "../data/osm_dk_20140101-transformed-32d.emb",
    'embNormal32Path': "../data/osm_dk_20140101-normal-32d.emb",
}

config = {
    'embedding_path': "",
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
    'remove_features': ['min_from_midnight', 'speed', 'acceleration', 'deceleration']
}

def_features = ['batch_size', 'epochs', 'hidden_layers', 'cells_per_layer', 'initial_dropout', 'dropout', 'activation', 'kernel_initializer', 'optimizer', 'target_feature', 'remove_features']