import pandas as pd

def read_data(datapath, emb_path):
    # Read features from segment-based csv, expects at least the startpoint, endpoint and segmentkey columns.
    df = pd.read_csv(datapath, header=0)

    # Read embeddings obtained from normal graph.
    # Expects columns: point, emb_1, ..., emb_N for N dimensions
    emb_df = pd.read_csv(emb_path, header=0, sep=' ')

    df = pd.merge(df, emb_df, left_on='startpoint', right_on='point').drop(['startpoint', 'point'], axis=1)
    df = pd.merge(df, emb_df, left_on='endpoint', right_on='point').drop(['endpoint', 'point'], axis=1)
    savepath = datapath[:-4] + '_with_normal_embeddings_accelpredict.csv'
    df.to_csv(savepath)

    return 'Saved dataframe to: %s' % savepath

print(read_data(datapath="C:\\P9Repos\\models\\data\\DataSpeedWindSeparate.csv", emb_path="C:\\Users\\Bjarke\\Desktop\\snap-master\\examples\\node2vec\\osm_dk_20140101-normal-32d.emb"))
