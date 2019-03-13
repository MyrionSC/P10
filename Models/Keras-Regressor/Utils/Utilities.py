from typing import List
from Utils.Configuration import Config
from Utils.Configuration import paths
import json


# Get the possible categories of a feature based on the column key
def get_cats(key: str) -> List[str]:
    if key == 'categoryid':
        return ['10', '11', '15', '16', '20', '21', '25', '26', '30', '31', '35', '40', '45', '50', '55', '60', '65']
    elif key == 'month':
        return ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    elif key == 'weekday':
        return ['1', '2', '3', '4', '5', '6', '7']


def model_dir_name(config: Config) -> str:
    return config['batch_dir'] + config['model_name_base'] + '/'


def model_path(config: Config) -> str:
    return paths['modelDir'] + model_dir_name(config)


def embedding_path(config: Config) -> str:
    if config["embedding"] is not None:
        return '{0}{1}.emb'.format(paths['embeddingDir'], config['embedding'])
    else:
        return "None"


def printparams(config: Config):
    print("Parameters used:")
    for key in sorted(config):
        print(" - " + key + ": " + str(config[key]))
    print()


def load_speed_config(energy_config: Config) -> Config:
    with open(energy_config['speed_model_path'] + "/config.json") as configFile:
        speed_config = json.load(configFile)
    return speed_config


def load_config(path: str) -> Config:
    with open(path + "/config.json") as file:
        config = json.load(file)
    return config
