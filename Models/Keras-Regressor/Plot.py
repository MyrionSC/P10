from Plots import plot_history, load_hist
import sys

args = sys.argv[1:]
model_path = args[0]
config, history = load_hist(model_path)
plot_history(history, config)
