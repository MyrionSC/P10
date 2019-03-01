from Plots import plot_history, load_hist
import sys

help = "Usage: Argument 1 to n should be paths to models. The plots end up in MODEL_DIR/plots."
if len(sys.argv) < 2:
    print(help)
    exit()



args = sys.argv[1:]
model_path = args[0]
config, history = load_hist(model_path)
plot_history(history, config)
