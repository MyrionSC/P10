import pandas as pd
import sklearn.metrics as m
from sklearn.model_selection import train_test_split
from math import sqrt
import sys

data_path = "../data/Data.csv"

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

class Baseline():
    def __init__(self):
        self.scalars = None

    def fit(self, feature, label):
        self.scalars = feature.groupby(['categoryid']).apply(lambda x: (label / x['segment_length']).mean()).to_frame('scalar')

    def predict(self, feature):
        if self.scalars is None:
            print("Model not trained")
            return None
        else:
            df = feature.join(self.scalars, on="categoryid")
            df['pred_ev'] = (df['segment_length'] * df['scalar'])
            return df['pred_ev']

    def save(self):
        if self.scalars is None:
            print("Model not trained")
        else:
            self.scalars.to_csv("model.csv", sep=",", encoding="utf8", decimal=".")

    def load(self):
        self.scalars = pd.read_csv("model.csv", sep=",", encoding="utf8", decimal=".").set_index("categoryid")

def root_mean_squared_error(y_true, y_pred):
    return sqrt(m.mean_squared_error(y_true, y_pred))

df = pd.read_csv(data_path, header=0)
label = df['ev_wh']
features = df[['segment_length', 'categoryid']]

if(sys.args[1] == "train"):
    X_train, X_test, Y_train, Y_test = train_test_split(features, label, test_size=0.3, random_state=1337)

    estimator = Baseline()
    estimator.fit(X_train, Y_train)
    estimator.save()

    train_pred = estimator.predict(X_train)
    test_pred = estimator.predict(X_test)

    print("Validation results:")
    print("MAE: {:f}".format(m.mean_absolute_error(Y_test, test_pred)))
    print("MSE: {:f}".format(m.mean_squared_error(Y_test, test_pred)))
    print("RMSE: {:f}".format(root_mean_squared_error(Y_test, test_pred)))
    print("R2: {:f}".format(m.r2_score(Y_test, test_pred)))
    print("")
    print("Training results:")
    print("MAE: {:f}".format(m.mean_absolute_error(Y_train, train_pred)))
    print("MSE: {:f}".format(m.mean_squared_error(Y_train, train_pred)))
    print("RMSE: {:f}".format(root_mean_squared_error(Y_train, train_pred)))
    print("R2: {:f}".format(m.r2_score(Y_train, train_pred)))

elif(sys.args[1] == "predict"):
    model = Baseline()
    model.load()

    prediction = model.predict(features)

    df = load_columns(data_path, columns=['mapmatched_id', 'segment_length', 'trip_id'])

    for i, target in enumerate(["ev_wh"]):
        target_predict = str(target + "_prediction")
        df[target_predict] = prediction
        df[target] = label
        prediction_df = df[['mapmatched_id', target_predict]].copy()
        prediction_file_path = target + "_prediction.csv"
        prediction_df.to_csv(prediction_file_path, index=False)

    column = df.columns

    grouped_df = df.groupby('trip_id')[column[3:]].sum()
    trip_r2 = m.r2_score(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    trip_mae = m.mean_absolute_error(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    trip_rmse = root_mean_squared_error(grouped_df['ev_wh'], grouped_df['ev_wh_prediction'])
    segment_r2 = m.r2_score(label, prediction)
    segment_mae = m.mean_absolute_error(label, prediction)
    segment_rmse = root_mean_squared_error(label, prediction)

    print("Trips:")
    print("R2: " + str(trip_r2))
    print("MAE: " + str(trip_mae))
    print("RMSE: " + str(trip_rmse))

    print("Segments:")
    print("R2: " + str(segment_r2))
    print("MAE: " + str(segment_mae))
    print("RMSE: " + str(segment_rmse))