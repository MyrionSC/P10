import pandas as pd
import sklearn.metrics as m
from sklearn.model_selection import train_test_split
from math import sqrt
import sys
from LocalSettings import main_db
import psycopg2
from psycopg2.extras import RealDictCursor
import csv

data_path = "../data/Data.csv"
train_path = "../data/Training.csv"
val_path = "../data/Test.csv"

def query(qry, db):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'], db['port'], db['host'], db['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(qry)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows)


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


def get_segment_features():
    qry = """
        SELECT segmentkey, meters as segment_length, categoryid
        FROM maps.osm_dk_20140101
        WHERE cateogory != 'ferry'
        ORDER BY segmentkey
    """

    df = query(qry, main_db)

    return df[['segmentkey']], df[['segment_length', 'categoryid']]


class Baseline():
    def __init__(self):
        self.scalars = None

    def fit(self, feature, label):
        print("Training model!")
        self.scalars = feature.groupby(['categoryid']).apply(lambda x: (label / x['segment_length']).mean()).to_frame('scalar')
        print("Model trained!")

    def predict(self, feature):
        if self.scalars is None:
            print("Can't predict: Model not trained")
            return None
        else:
            print("Predicting energy consumptions!")
            df = feature.join(self.scalars, on="categoryid")
            df['pred_ev'] = (df['segment_length'] * df['scalar'])
            print("Energy consumption predicted!")
            return df[['pred_ev']]

    def save(self):
        if self.scalars is None:
            print("Model not trained")
        else:
            self.scalars.to_csv("model.csv", sep=",", encoding="utf8", decimal=".")
            print("Model saved as model.csv")

    def load(self):
        self.scalars = pd.read_csv("model.csv", sep=",", encoding="utf8", decimal=".").set_index("categoryid")
        print("Model loaded from model.csv")

def root_mean_squared_error(y_true, y_pred):
    return sqrt(m.mean_squared_error(y_true, y_pred))

if len(sys.argv) != 2:
    print("There must be one argument: train, predict or segments!")
    quit()
if not (sys.argv[1] == 'train' or sys.argv[1] == 'predict' or sys.argv[1] == 'segments'):
    print("Argument must be either train, predict or segments!")
    quit()

if not sys.argv[1] == 'segments':
    df = pd.read_csv(train_path, header=0)
    Y_train = df['ev_kwh']
    X_train = df[['segment_length', 'categoryid']]
    trip_id = df['trip_id']
    df = pd.read_csv(val_path, header=0)
    Y_test = df['ev_kwh']
    X_test = df[['segment_length', 'categoryid']]
    val_trip_id = df['trip_id']


if(sys.argv[1] == "train"):
    #X_train, X_test, Y_train, Y_test = train_test_split(features, label, test_size=0.3, random_state=1337)

    estimator = Baseline()
    estimator.fit(X_train, Y_train)
    estimator.save()

    train_pred = estimator.predict(X_train)
    test_pred = estimator.predict(X_test)

    df_train, df_test = pd.DataFrame(), pd.DataFrame()
    df_train["trip_id"] = trip_id
    df_train["act"] = Y_train
    df_train["pred"] = train_pred
    df_test["trip_id"] = val_trip_id
    df_test["act"] = Y_test
    df_test["pred"] = test_pred

    grp_train = df_train.groupby('trip_id').sum()
    grp_test = df_test.groupby('trip_id').sum()

    metrics = {
        "MAE": m.mean_absolute_error(df_train["act"], df_train["pred"]),
        "RMSE": root_mean_squared_error(df_train["act"], df_train["pred"]),
        "R2": m.r2_score(df_train["act"], df_train["pred"]),
        "val_MAE": m.mean_absolute_error(df_test["act"], df_test["pred"]),
        "val_RMSE": root_mean_squared_error(df_test["act"], df_test["pred"]),
        "val_R2": m.r2_score(df_test["act"], df_test["pred"]),
        "MAE tur": m.mean_absolute_error(grp_train["act"], grp_train["pred"]),
        "RMSE tur": root_mean_squared_error(grp_train["act"], grp_train["pred"]),
        "R2 tur": m.r2_score(grp_train["act"], grp_train["pred"]),
        "val_MAE tur": m.mean_absolute_error(grp_test["act"], grp_test["pred"]),
        "val_RMSE tur": root_mean_squared_error(grp_test["act"], grp_test["pred"]),
        "val_R2 tur": m.r2_score(grp_test["act"], grp_test["pred"])
    }

    with open("batch_metrics.csv", "w") as f:
        w = csv.DictWriter(f, metrics.keys())
        w.writeheader()
        w.writerows(metrics)

    print("Validation results:")
    print("MAE: {:f}".format(metrics["val_MAE"]))
    print("MSE: {:f}".format(m.mean_squared_error(Y_test, test_pred)))
    print("RMSE: {:f}".format(metrics["val_RMSE"]))
    print("R2: {:f}".format(metrics["val_R2"]))
    print("")
    print("Training results:")
    print("MAE: {:f}".format(metrics["MAE"]))
    print("MSE: {:f}".format(m.mean_squared_error(Y_train, train_pred)))
    print("RMSE: {:f}".format(metrics["RMSE"]))
    print("R2: {:f}".format(metrics["R2"]))

elif(sys.argv[1] == "predict"):
    model = Baseline()
    model.load()

    prediction = model.predict(features)

    df = load_columns(data_path, columns=['mapmatched_id', 'segment_length', 'trip_id'])

    for i, target in enumerate(["ev_kwh"]):
        target_predict = str(target + "_prediction")
        df[target_predict] = prediction
        df[target] = label
        prediction_df = df[['mapmatched_id', target_predict]].copy()
        prediction_file_path = target + "_prediction.csv"
        prediction_df.to_csv(prediction_file_path, index=False)

    column = df.columns

    grouped_df = df.groupby('trip_id')[column[3:]].sum()
    trip_r2 = m.r2_score(grouped_df['ev_kwh'], grouped_df['ev_kwh_prediction'])
    trip_mae = m.mean_absolute_error(grouped_df['ev_kwh'], grouped_df['ev_kwh_prediction'])
    trip_rmse = root_mean_squared_error(grouped_df['ev_kwh'], grouped_df['ev_kwh_prediction'])
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
 
elif(sys.argv[1] == "segments"):
    model = Baseline()
    model.load()

    keys, features = get_segment_features()
    predictions = model.predict(features)
    predictions['segmentkey'] = keys
    predictions = predictions.reindex(['segmentkey', 'pred_ev'], axis=1)
    predictions.to_csv("segment_predictions.csv" , index=False)
