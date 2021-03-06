import pandas as pd
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.pyplot import *
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from Utils.Utilities import model_path
import os
import json
from Utils.Configuration import Config

plt.rcParams.update({'mathtext.fontset': 'stix'})
plt.rcParams.update({'font.family': 'STIXGeneral'})
plt.rcParams.update({'font.size': 30})
plt.rcParams.update({'figure.figsize': (15, 10)})

categories = {1: 'ferry',
              10: 'motorway',
              11: 'motorway_link',
              15: 'trunk',
              16: 'trunk_link',
              20: 'primary',
              21: 'primary_link',
              25: 'secondary',
              26: 'secondary_link',
              30: 'tertiary',
              31: 'tertiary_link',
              35: 'unclassified',
              40: 'residential',
              45: 'living_street',
              50: 'service',
              55: 'road',
              60: 'track',
              65: 'unpaved'}


def plot_history(history, config):
    modelpath = model_path(config)
    if not os.path.isdir(modelpath + "plots/"):
        os.makedirs(modelpath + "plots/")
    with PdfPages(modelpath + '/plots/' + config['model_name_base'] + '_combined.pdf') as pdf:
        for key in [x for x in sorted(history) if not x.startswith('val') and "r2" not in x and 'trip' not in x]:
            midvalue = history[key][int(len(history[key]) / 2)]
            lastvalue = history[key][-1]
            delta = abs(midvalue - lastvalue)

            plt.plot(range(2, len(history[key]) + 1), history[key][1:], 'b-', label="Trænings " + key)
            plt.plot(range(2, len(history[key]) + 1), history['val_' + key][1:], 'r-', label="Validerings " + key)
            plt.xlabel("Epoker")
            plt.ylabel(key.capitalize())
            plt.title(key.capitalize() + " i løbet af træning")

            plt.ylim(lastvalue - delta * 0.5, lastvalue + delta * 4)
            plt.legend()
            plt.tight_layout()
            plt.savefig(modelpath + "plots/" + config['model_name_base'] + "_" + key + ".pdf", bbox_inches='tight')
            pdf.savefig()
            plt.clf()
            plt.close()


def load_hist(model_path):
    with open(model_path + "/config.json", "r") as f:
        config = json.load(f)
    with open(model_path + "/history.json", "r") as f:
        history = json.load(f)
    return config, history


def load_history(config: Config):
    modelpath = model_path(config)
    if not os.path.isfile(modelpath + 'history.json'):
        return None
    with open(modelpath + 'history.json', "r") as f:
        hist = json.loads(f.read())
    return hist


def r2_count_pd(df_in):
    r2 = r2_score(df_in['y_true'], df_in['y_pred'])
    count = len(df_in)
    return pd.Series(dict(r2=r2, count=count))


def r2_pd(df_in):
    return pd.Series(dict(r2=r2_score(df_in['y_true'], df_in['y_pred'])))


def mae_pd(df_in):
    return pd.Series(dict(mae=mean_absolute_error(df_in['y_true'], df_in['y_pred'])))


def r2_by_frequency(df, count=False):
    df2 = df.dropna()
    print("Calculating trip segment frequency")
    df2 = df2.join(pd.DataFrame(df2['segmentkey'].value_counts()).rename(columns={'segmentkey': 'frequency'}), on='segmentkey')
    print("Calculating R^2")
    if count:
        df2 = df2.groupby(['frequency']).apply(r2_count_pd).reset_index()
        df2['count'] = (df2['count']).astype(int)
    else:
        df2 = df2.groupby(['frequency']).apply(r2_pd).reset_index()

    plt.clf()
    fig, ax1 = plt.subplots(figsize=(15, 10))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ln1 = ax1.plot(df2['frequency'], df2['r2'], '-', label='R^2 score')
    ax1.set_xlabel("Frequency")
    ax1.set_ylabel("R^2 score")

    if count:
        ax2 = ax1.twinx()
        ln2 = ax2.plot(df2['frequency'], df2['count'], 'r:', label='Number of data points')
        ax2.set_ylabel("Number of data points")

    ax1.legend()
    ax1.grid()
    fig.tight_layout()
    fig.show()


def r2_by_category(df):
    df2 = df.dropna()
    print("Calculating R^2")
    df2 = df2.groupby(['categoryid']).apply(r2_pd).reset_index()
    df2 = df2.sort_values(by=["r2"], ascending=False)
    df2['category'] = df2['categoryid'].map(lambda x: categories[x].replace('_', ' ').capitalize())

    fig, ax1 = plt.subplots(figsize=(15, 10))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ln1 = ax1.bar(df2['category'], df2['r2'], label='R^2 score')
    ax1.set_xlabel("Category")
    ax1.set_ylabel("R^2 score")
    plt.xticks(rotation=90)
#   range(len(df2['category'])), df2['category'],
    ax1.legend()
    ax1.grid()
    fig.tight_layout()
    fig.show()


def mae_by_category(df):
    df2 = df.dropna()
    print("Calculating R^2")
    df2 = df2.groupby(['categoryid']).apply(mae_pd).reset_index()
    df2 = df2.sort_values(by=["mae"], ascending=False)
    df2['category'] = df2['categoryid'].map(lambda x: categories[x].replace('_', ' ').capitalize())

    fig, ax1 = plt.subplots(figsize=(15, 10))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ln1 = ax1.bar(df2['category'], df2['mae'], label='Mean Absolute Error')
    ax1.set_xlabel("Category")
    ax1.set_ylabel("Mean Absolute Error")
    plt.xticks(rotation=90)
    #   range(len(df2['category'])), df2['category'],
    ax1.legend()
    ax1.grid()
    fig.tight_layout()
    fig.show()


if __name__ == '__main__':
    help = "Usage: Argument 1 to n should be paths to models. The plots end up in MODEL_DIR/plots."
    if len(sys.argv) < 2:
        print(help)
        exit()

    modelPaths = sys.argv[1:]
    for mp in modelPaths:
        print("Creating plots for " + mp + ". Plots can be found in " + mp + "plots.")
        config, history = load_hist(mp)
        plot_history(history, config)