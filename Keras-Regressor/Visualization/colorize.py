import numpy as np
import sklearn
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import time
from colorsys import hsv_to_rgb

emb_transformed_path = '../../data/osm_dk_20140101-transformed-32d.emb'
proj_path = '../../data/osm_dk_20140101-transformed-32d-TSNE.csv'

emb_df = pd.read_csv(emb_transformed_path, header=0, sep=' ', index_col=0)
proj = pd.read_csv(proj_path, header=0, sep=',', index_col=0)

# Convert from Carthesian to polar coordinates
angles = (np.angle(proj["0"] + (proj["1"] * 1j), True) + 180) % 360
distance = (MinMaxScaler().fit_transform(np.abs(proj["0"].values + (proj["1"].values * 1j)).reshape(-1, 1))).reshape(1, -1)[0]
packaged = pd.DataFrame(np.stack([angles / 360, distance], axis=1), emb_df.index, ["hue", "saturation"])

colors = np.apply_along_axis(lambda row: hsv_to_rgb(row[0], row[1], 1), 1, packaged)

plt.scatter(proj["0"], proj["1"], c=colors)
plt.show()

segmentproj = pd.DataFrame(colors, packaged.index, ["r", "g", "b"])
segmentproj.to_csv(proj_path + ".colors")
