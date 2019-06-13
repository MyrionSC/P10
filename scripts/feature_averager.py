import pandas as pd

df = pd.read_csv("batch_metrics_avg.csv", header=0, sep=',', decimal='.')
cols = list(df)[1:]
df['incline'] = ~df['model_name'].str.contains('Incline')
df['type'] = df['model_name'].str.contains('type')
df['traffic_lights'] = df['model_name'].str.contains('traffic_lights')
df['cats'] = df['model_name'].str.contains('cat_start')
df['direction'] = df['model_name'].str.contains('direction')

fts = ['cats', 'incline', 'direction', 'traffic_lights', 'type']
dfs = {x: df.groupby(df[x]).mean() for x in fts}

for k, v in dfs.items():
	v['name'] = k
	v.loc[v.index == True, 'name'] = "with_" + k
	v.loc[v.index == False, 'name'] = "no_" + k
	v = v.set_index('name')
	dfs[k] = v[cols]

df2 = pd.concat(dfs.values())

df2.to_csv("features_avg.csv", sep=',', header=True, index=True, decimal='.')