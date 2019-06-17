from DNNRegressor import predict
import batch_configs.superseg_features_grid
import batch_configs.superseg_features_grid_with_inc

configs = batch_configs.superseg_features_grid.configs + batch_configs.superseg_features_grid_with_inc.configs

first = True
for conf in configs:
    if "Iter1" in conf['model_name_base']:
        predict(conf, False, first)
        first = False
