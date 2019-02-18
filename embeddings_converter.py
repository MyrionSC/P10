import pandas as pd


names = ['segmentkey'] + ['emb_' + str(i) for i in range(20)]
name = "osm_dk_20140101-LINE-transformed-20d"

df = pandas.read_csv(name + ".emb", sep=" ", header=None, names=names, index_col=False, skiprows=1, encoding="utf8", decimal='.')
df.sort_values(['segmentkey']).to_csv(name + ".csv", sep=",", header=True, index=False, encoding="utf8", decimal='.')