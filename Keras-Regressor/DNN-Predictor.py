from Utils import loadScaler, read_data, load_model
from config import *
from sqlalchemy import create_engine
from Plots import *
from sklearn.metrics import mean_squared_error
from math import sqrt
import pandas as pd
from Metrics import rmse
import csv
import os
import json

#from LocalSettings import database

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


# def upload_to_database(df, db_schema, db_table, column='ev_wh'):
#     """
#         Uploads results to databse (db_schema.db_table) using pandas
#         .to_sql() method
#
#         Args:
#             df (pd.DataFrame): DataFrame to be uploaded to DB
#             db_schema (str)  : schema name in DB
#             db_table (str)   : table name in DB
#
#         Returns:
#             None
#     """
#
#     # psycopg2 configguration
#     engine = create_engine(f'postgresql+psycopg2://{database['username']}:{database['password']}@{database['host']}:{database['port']}/{database['name']}')
#     connection = engine.raw_connection()
#
#     try:
#
#         cursor = connection.cursor()
#
#         # 1) drop previous index
#         cursor.execute('DROP INDEX IF EXISTS %s.%s_%s_mapmatched_id_idx;' % (db_schema, db_schema, db_table))
#         connection.commit()
#         print('Dropped index: %s.%s_%s_mapmatched_id_idx;' % (db_schema, db_schema, db_table))
#
#         # 2) upload data
#         # 2.1) truncate table
#         cursor.execute('TRUNCATE %s.%s' % (db_schema, db_table))
#         connection.commit()
#         # 2.2) insert data into DB
#         dataText = b','.join(cursor.mogrify(b'(%s,%s)', (index, float(row[column]))) for index, row in df.iterrows())
#
#         query_str = b'INSERT INTO ' + db_schema.encode() + b"." + db_table.encode() + b" VALUES "
#         cursor.execute(query_str + dataText)
#         connection.commit()
#         print('Finished uploading data to %s.%s;' % (db_schema, db_table))
#
#         # 3) add index
#         cursor.execute(""CREATE INDEX {0}_{1}_mapmatched_id_idx
#                           ON {0}.{1} USING btree (mapmatched_id)
#                           TABLESPACE pg_default;"".format(db_schema, db_table))
#         print('Created index: %s_%s_mapmatched_id_idx;' % (db_schema, db_table))
#
#         cursor.close()
#         connection.commit()
#     except Exception as e:
#         raise e
#     finally:
#         connection.close()


features, labels, num_features, num_labels, _, trip_ids = read_data(paths['dataPath'], config['target_feature'], config['remove_features'], scale=True, load_scaler=True)
modelPath = ("saved_models/DNNRegressor")# %s%s - %s" % (target_feature_string, embeddings_used_string, param_string))

model = load_model(modelPath)

model.compile(loss='mean_squared_error', optimizer=config['optimizer'], metrics=['mae', 'mse', 'mape', rmse])
prediction = model.predict(features, batch_size=config['batch_size'], verbose=1)
evaluation = model.evaluate(features, labels, batch_size=config['batch_size'], verbose=1)

r2 = r2_score(labels, prediction)
print("R2: " + str(r2))

# Save history
history_output_path = ("saved_history/Test_Predicting.json")# %s%s - %s.json" % (target_feature_string, embeddings_used_string, param_string))
history_json = json.dumps(evaluation)
if not os.path.isdir("saved_history"):
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
    prediction_file_path = "../data/test_" + target + "_prediction.csv"
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