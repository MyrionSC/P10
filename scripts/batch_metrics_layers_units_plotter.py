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

def plot(name, dct, layers, units, pdf=None, path=None):
    fig, ax1 = plt.subplots()
    cmap = cm.get_cmap('coolwarm')
    if "R^2" in name:
        cmap = reverse_colormap(cmap, 'warmcool')
    plt.imshow(dct, cmap=cmap, interpolation='nearest', aspect='auto')
    plt.yticks(range(len(layers)), layers)
    plt.xticks(range(len(units)), units)
    for i in range(len(layers)):
        for j in range(len(units)):
            if dct[i, j] > 0:
                text = ax1.text(j, i, "{:.4f}".format(dct[i, j]),
                               ha="center", va="center", color="black")

    plt.xlabel("Antal neuroner per lag")
    plt.ylabel("Antal lag")
    plt.title(name)
    plt.tight_layout()
    #plt.colorbar()
    if pdf is not None:
        pdf.savefig()
    if path is not None:
        plt.savefig(os.path.dirname(path) + '/LU_' + name.replace(" ", "_").replace("^", "").replace("æ", "ae").replace("å", "aa").replace("ø", "oe") + '.pdf')
    plt.clf()
    plt.close()

def main(args):
    if not len(args) == 2:
        print("Invalid number of arguments: got " + str(len(args)) + " expected 2.")
        quit(-1) 
    if not os.path.isfile(args[1]):
        print("File not found: " + os.path.abspath(args[1]))
        quit(-1)
    if not args[0] in ["mean_absolute_error", "mean_squared_error", "rmse", "mean_absolute_percentage_error", "r2", "loss", "all"]:
        print("Invalid evaluation metric " + args[0] + " expected 1 of " + str(["mean_absolute_error", "mean_squared_error", "rmse", "mean_absolute_percentage_error", "r2", "loss", "all"]))
        quit(-1)

    df = pd.read_csv(args[1], delimiter=",", decimal=".", header=0)
    df.columns = df.columns.str.strip()
    df['layers'] = df.model_name.map(lambda x: int(re.findall("[0-9]*Layers", x)[0][:-6]))
    df['units'] = df.model_name.map(lambda x: int(re.findall("[0-9]*Units", x)[0][:-5]))
    layers = sorted(df.layers.unique())
    units = sorted(df.units.unique())

    plt.rcParams.update({'mathtext.fontset': 'stix'})
    plt.rcParams.update({'font.family': 'STIXGeneral'})
    plt.rcParams.update({'font.size' : 15})

    if args[0] != "all":
        do_plots(df, layers, units, args[0], args[1])
    else:
        for metric in ["mean_absolute_error", "mean_squared_error", "rmse", "mean_absolute_percentage_error", "r2", "loss"]:
            do_plots(df, layers, units, metric, args[1])

def shorthand(metric):
    if metric == 'mean_absolute_error':
        return 'mae'
    if metric == 'mean_absolute_percentage_error':
        return 'mape'
    if metric == 'mean_squared_error':
        return 'mse'
    else:
        return metric

def title_str(metric):
    if metric == 'r2':
        return 'R^2'
    if metric == 'loss':
        return 'Loss'
    return shorthand(metric).upper()


def do_plots(df, layers, units, metric, path):
    if metric == 'r2':
        dct_val = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_' + metric].values[0] for unit in units] for layer in layers])
        dct_train = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['train_' + metric].values[0] for unit in units] for layer in layers])
        dct_val_trip = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_trip_' + shorthand(metric)].values[0] for unit in units] for layer in layers])
        dct_train_trip = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['train_trip_' + shorthand(metric)].values[0] for unit in units] for layer in layers])
    elif metric == 'loss':
        dct_val = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_' + metric].values[0] for unit in units] for layer in layers])
        dct_train = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit][metric].values[0] for unit in units] for layer in layers])
    else:
        dct_val = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_' + metric].values[0] for unit in units] for layer in layers])
        dct_train = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit][metric].values[0] for unit in units] for layer in layers])
        dct_val_trip = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['val_trip_' + shorthand(metric)].values[0] for unit in units] for layer in layers])
        dct_train_trip = np.array([[df.loc[df['layers'] == layer].loc[df['units'] == unit]['train_trip_' + shorthand(metric)].values[0] for unit in units] for layer in layers])
    
    with PdfPages(os.path.dirname(path) + '/LU_All_' + metric + '.pdf') as pdf:
        plot("Trænings " + title_str(metric), dct_train, layers, units, pdf, path)
        plot("Validerings " + title_str(metric), dct_val, layers, units, pdf, path)
        if metric != 'loss':
            plot("Trænings " + title_str(metric) + " på ture", dct_train_trip, layers, units, pdf, path)
            plot("Validerings " + title_str(metric) + " på ture", dct_val_trip, layers, units, pdf, path)

if __name__ == "__main__":
    main(sys.argv[1:])