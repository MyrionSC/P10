import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.colors as plt_colors
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import os
import sys
import re
import pprint

def reverse_colormap(cmap, name = 'my_cmap_r'):
    """
    In: 
    cmap, name 
    Out:
    my_cmap_r

    Explanation:
    t[0] goes from 0 to 1
    row i:   x  y0  y1 -> t[0] t[1] t[2]
                   /
                  /
    row i+1: x  y0  y1 -> t[n] t[1] t[2]

    so the inverse should do the same:
    row i+1: x  y1  y0 -> 1-t[0] t[2] t[1]
                   /
                  /
    row i:   x  y1  y0 -> 1-t[n] t[2] t[1]
    """        
    reverse = []
    k = []   

    for key in cmap._segmentdata:    
        k.append(key)
        channel = cmap._segmentdata[key]
        data = []

        for t in channel:                    
            data.append((1-t[0],t[2],t[1]))            
        reverse.append(sorted(data))    

    LinearL = dict(zip(k,reverse))
    my_cmap_r = plt_colors.LinearSegmentedColormap(name, LinearL) 
    return my_cmap_r

def plot(name, dct, layers, units, pdf=None):
    fig, ax1 = plt.subplots()
    plt.imshow(dct, cmap=reverse_colormap(cm.get_cmap('coolwarm'), 'warmcool'), interpolation='nearest', aspect='auto')
    plt.yticks(range(len(layers)), layers)
    plt.xticks(range(len(units)), units)
    for i in range(len(layers)):
        for j in range(len(units)):
            if dct[i, j] > 0:
                text = ax1.text(j, i, "{:.4f}".format(dct[i, j]),
                               ha="center", va="center", color="black")

    plt.xlabel("Neurons per hidden layer")
    plt.ylabel("Number of hidden layers")
    plt.title(name)
    plt.tight_layout()
    #plt.colorbar()
    if pdf is not None:
        pdf.savefig()
    plt.clf()
    plt.close()

def main(args):
    if not len(args) == 1:
        print("Invalid number of arguments: got " + str(len(args)) + " expected 1.")
        quit(-1) 
    if not os.path.isfile(args[0]):
        print("File not found: " + os.path.abspath(args[0]))
        quit(-1)

    df = pd.read_csv(args[0], delimiter=",", decimal=".", header=0)
    df.columns = df.columns.str.strip()
    df['layers'] = df.model_name.map(lambda x: int(re.findall("[0-9]*Layers", x)[0][:-6]))
    df['units'] = df.model_name.map(lambda x: int(re.findall("[0-9]*Units", x)[0][:-5]))
    layers = sorted(df.layers.unique())
    units = sorted(df.units.unique())
    print(list(df))
    dct_val = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_r2'].values[0] for unit in units] for layer in layers])
    dct_train = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['train_r2'].values[0] for unit in units] for layer in layers])
    dct_val_trip = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_trip_r2'].values[0] for unit in units] for layer in layers])
    dct_train_trip = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['train_trip_r2'].values[0] for unit in units] for layer in layers])

    plt.rcParams.update({'mathtext.fontset': 'stix'})
    plt.rcParams.update({'font.family': 'STIXGeneral'})
    plt.rcParams.update({'font.size' : 15})

    with PdfPages(os.path.dirname(args[0]) + '/layers_units_metrics.pdf') as pdf:
        plot("Training R^2", dct_train, layers, units, pdf)
        plot("Validation R^2", dct_val, layers, units, pdf)
        plot("Training Trip R^2", dct_train_trip, layers, units, pdf)
        plot("Validation Trip R^2", dct_val_trip, layers, units, pdf)

if __name__ == "__main__":
    main(sys.argv[1:])