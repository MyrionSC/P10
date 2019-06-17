import pandas as pd
df = pd.read_csv("category_measures.csv")
df = df.append(df[['MAE', 'MAE per meter', 'MAE/<E>', '<E>']].diff(periods=4)[4:])
df = df.reset_index()
df.loc[df['Origin'].isnull(), 'Origin'] = "Delta"
df.loc[df['Type'].isnull(), 'Type'] = df['Type'].shift(4)
df.to_csv("category_measures.csv")