import os
import sys
import pandas as pd

def main(args):
	if not len(args) == 1:
		print("Invalid number of arguments: got " + str(len(args)) + " expected 1.")
		quit(-1) 
	if not os.path.isfile(args[0] + "/batch_metrics.csv"):
		print("No batch metrics found in " + os.path.abspath(args[0]))
		quit(-1)
	df = pd.read_csv(args[0] + "/batch_metrics.csv", delimiter=",", decimal=".", header=0)
	df.model_name = df.model_name.map(lambda x : x[:-6])
	df = df.groupby(df.model_name).mean()
	df.to_csv(args[0] + "/batch_metrics_avg.csv", sep=",", decimal=".", header=True, index=True)

if __name__ == "__main__":
	main(sys.argv[1:])