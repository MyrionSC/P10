from LocalSettings import database
import psycopg2
from psycopg2.extras import RealDictCursor
from config import *
import pandas as pd
import datetime
from Utils import load_model, one_hot, scale_df

def query(str):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(database['name'], database['user'], database['port'], database['host'], database['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def predict_segment(segmentkey):
    qry = """
        SELECT osm.categoryid, inc.incline, osm.meters as segment_length, spd.speedlimit
        FROM maps.osm_dk_20140101 osm
        JOIN experiments.mi904e18_segment_incline inc
        ON osm.segmentkey = inc.segmentkey
        JOIN experiments.mi904e18_speedlimits spd
        ON osm.segmentkey = spd.segmentkey
        WHERE osm.segmentkey = {0}
    """.format(segmentkey)

    features = pd.DataFrame(query(qry))

    now = datetime.datetime.today()
    features['month'] = now.month
    features['weekday'] = now.weekday()
    features['quarter'] = (now.hour * 4) + int(now.minute / 15)
    features = features[config['feature_order']]
    features = features.applymap(str)

    features = one_hot(pd.DataFrame(features))
    features = scale_df(features)

    estimator = load_model(paths['modelDir'] + config['model_name'])

    res = estimator.predict(features)
    return res[0][0]

print(predict_segment(386273))