#!/usr/bin/env python3
from LocalSettings import database
from Configuration import *
import pandas as pd
from Utils import load_model, current_time, one_hot, scale_df, embedding_path, merge_embeddings, query
import time


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
    features = pd.DataFrame(query(qry))
    keys = features['segmentkey']

    # Include current time features
    features['month'], features['weekday'], features['quarter'] = current_time()

    # Ensure correct order of dataframe
    features = features[['segmentkey'] + config['feature_order']]

    # Preprocess data to same format as trained on
    features = one_hot(features)

    if config['embeddings_used'] is not None:
        emb_df = get_embeddings(segments)
        features = merge_embeddings(features, emb_df).drop(['segmentkey'], axis=1)

    features = scale_df(features, load_scaler=True)

    # Load model
    estimator = load_model(paths['modelDir'] + config['model_name'])

    # Return prediction
    res = pd.DataFrame(estimator.predict(features), columns=['ev_wh']).set_index(keys)
    return res


def get_embeddings(segments):
    print("Getting embeddings")
    start = time.time()
    temp = segments.copy()
    with open(embedding_path(), "r") as f:
        f.readline()
        df = pd.DataFrame(columns=['segmentkey'] + ['emb_' + str(x) for x in range(embedding_config[config['embeddings_used']]['dims'])])

        for line in f:
            for seg in temp:
                if line.startswith(str(seg) + " "):
                    df2 = pd.DataFrame([line.strip().split(" ")], columns=list(df))
                    df = df.append(df2)
                    temp.remove(seg)
                    break
            if not temp:
                break
    print("Time %s" % (time.time() - start))
    df['segmentkey'] = df['segmentkey'].map(int)
    return df.set_index(['segmentkey'])


print(predict(list(range(1, 1000))))
