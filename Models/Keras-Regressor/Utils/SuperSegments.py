import pandas as pd
from Utils.SQL import supersegment_qry, read_query
from Utils.Utilities import get_cats
from Utils.LocalSettings import main_db


def general_converter(num_segments, limit=None):
    qrt = supersegment_qry(num_segments, limit)

    df = pd.DataFrame(read_query(qrt, main_db))

    for cat in get_cats('categoryid'):
        df['categoryid_' + cat] = df['segment1_length'] * df['category1'].map(lambda x: 1 if x == int(cat) else 0)
        for i in range(2, num_segments + 1):
            df['categoryid_' + cat] = df['categoryid_' + cat] + df['segment' + str(i) + '_length'] * df[
                'category' + str(i)].map(lambda x: 1 if x == int(cat) else 0)
        df['categoryid_' + cat] = df['categoryid_' + cat] / df['supersegment_length']

    for i in range(1, num_segments + 1):
        df = df.drop(['segment' + str(i) + '_length', 'category' + str(i)], axis=1)

    return df.set_index(['trip_id', 'supersegmentno'])