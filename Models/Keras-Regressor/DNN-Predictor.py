from Utils import read_data, load_model
from configs import *
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from math import sqrt
import pandas as pd
from Metrics import rmse
import os
import json
import time


def load_columns(filename, columns=[], index=None):
    """
        Loads columns  into pandas DataFrame object
        from specified .csv file;

        Args:
            filename (str): name of .csv file
            columns (list): list of columns to load
            index    (str): name of index
        Returns:
            df (pd.DataFrame) : pandas DataFrame with one column (index) set as index
    """
    df = pd.read_csv(filename)
    df = df[columns]

    if index is not None:
        df.set_index('mapmatched_id', inplace=True)

    return df


print("")
print("------ Reading data ------")
start_time = time.time()
features, labels, num_features, num_labels, trip_ids = read_data(paths['dataPath'], scale=True,
                                                                 use_speed_prediction=not speed_predictor)
print("Data read, time elapsed: %s" % (time.time() - start_time))

modelPath = (paths['modelDir'] + config['model_name'])

model = load_model(modelPath)

model.compile(loss='mean_squared_error', optimizer=config['optimizer'], metrics=['mae', 'mse', 'mape', rmse])
prediction = model.predict(features, batch_size=config['batch_size'], verbose=1)
evaluation = model.evaluate(features, labels, batch_size=config['batch_size'], verbose=1)

r2 = r2_score(labels, prediction)
print("R2: " + str(r2))

# Save history
history_output_path = (paths['historyDir'] + config['model_name'] + "_Predictions.json")
history_json = json.dumps(evaluation)
if not os.path.isdir(paths['historyDir']):
    os.makedirs(os.path.dirname(history_output_path))
with open(history_output_path, "w") as f:
    f.write(history_json)

# go over predictions saving them into pandas DataFrame
df = load_columns(paths['dataPath'], columns=['mapmatched_id', 'segment_length', 'trip_id'])

for i, target in enumerate(config['target_feature']):
    target_predict = str(target + "_prediction")
    df[target_predict] = pd.Series(prediction[:, i])
    df[target] = labels[target]
    prediction_df = df[['mapmatched_id', target_predict]].copy()
    prediction_file_path = "../data/" + target + "_prediction.csv"
    prediction_df.to_csv(prediction_file_path, index=False)

column = df.columns

if 'ev_wh' in config['target_feature']:
    grouped_df = df.groupby('trip_id')[column[3:]].sum()
    grouped_r2 = r2_score(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    grouped_mae = mean_absolute_error(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    grouped_rmse = sqrt(mean_squared_error(grouped_df['ev_wh'], grouped_df['ev_wh_prediction']))
    print(grouped_r2)
    print(grouped_mae)
    print(grouped_rmse)
elif 'speed' in config['target_feature']:
    df['seconds'] = df['segment_length']/df['speed']
    df['seconds_prediction'] = df['segment_length']/df['speed_prediction']
    grouped_df = df.groupby('trip_id')['seconds', 'seconds_prediction'].sum()

# print("Prediction, actual, difference, relative")
# for pred, truth in zip(prediction, labels.values):
#     #output = str(pred[0]) + " - " + str(truth) + " - " + str(abs(pred[0]-truth)) + " - " + str(pred[0] / truth)
#     print(str(pred[0]) + " - " + str(truth[0]) + " - " + str(pred[0] - truth[0]) + " - " + str(pred[0] / truth [0]))

# visualize the speed prediction results
# if 'ev_wh' in config['target_feature']:
#     target_index = config['target_feature'].index('ev_wh')
#     df = load_columns(paths['dataPath'], columns=['mapmatched_id', 'segmentkey', 'categoryid', 'ev_wh'], index='mapmatched_id')
#     df['y_true'] = df['ev_wh']
#     df['y_pred'] = pd.Series(prediction[:, target_index], index=df.index)
#     df = df.drop(columns=config['target_feature'])
#     # TODO: add call to plotting function here
#     r2_by_frequency(df)
#     r2_by_category(df)
#
# # visualize the speed prediction results
# if 'speed' in config['target_feature']:
#     target_index = config['target_feature'].index('speed')
#     df = load_columns(paths['dataPath'], columns=['mapmatched_id', 'segmentkey', 'categoryid', 'speed', 'speedlimit'], index='mapmatched_id')
#     df['y_true'] = df['speed']
#     df['y_pred'] = pd.Series(prediction[:, target_index], index=df.index)
#     #df = df.drop(columns=target_feature)
#     # TODO: add call to plotting function here
#     r2_by_category(df)
#     mae_by_category(df)
#
#     df['y_true'] = df['speedlimit']
#     r2_by_category(df)
#     mae_by_category(df)