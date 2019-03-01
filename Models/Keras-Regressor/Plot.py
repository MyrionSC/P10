from Plots import plot_history, load_hist
import sys

help = "Usage: Argument 1 to n should be paths to models. The plots end up in MODEL_DIR/plots."
if len(sys.argv) < 2:
    print(help)
    exit()

modelPaths = sys.argv[1:]
for mp in modelPaths:
    print("Creating plots for " + mp + ". Plots can be found in " + mp + "/plots.")
    config, history = load_hist(mp)
    plot_history(history, config)


