from LocalSettings import database
import psycopg2
from psycopg2.extras import RealDictCursor
from config import *
import pandas as pd
from Utils import load_model, current_time, preprocess_data


def query(str):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(database['name'], database['user'], database['port'], database['host'], database['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def predict(segments):
    if isinstance(segments, int):
        segments = [segments]
    qry = """
            SELECT osm.segmentkey, osm.categoryid, inc.incline, osm.meters as segment_length, spd.speedlimit
            FROM maps.osm_dk_20140101 osm
            JOIN experiments.mi904e18_segment_incline inc
            ON osm.segmentkey = inc.segmentkey
            JOIN experiments.mi904e18_speedlimits spd
            ON osm.segmentkey = spd.segmentkey
            WHERE osm.segmentkey = ANY(ARRAY [ {0} ])
    """.format(",".join([str(x) for x in segments]))
    features = pd.DataFrame(query(qry)).applymap(str)
    keys = features['segmentkey']

    # Include current time features
    features['month'], features['weekday'], features['quarter'] = current_time()

    # Ensure correct order of dataframe
    features = features[config['feature_order']]

    # Preprocess data to same format as trained on
    features = preprocess_data(features)

    # Load model
    estimator = load_model(paths['modelDir'] + config['model_name'])

    # Return prediction
    res = pd.DataFrame(estimator.predict(features), columns=['ev_wh']).set_index(keys)
    return res


print(predict(1))
