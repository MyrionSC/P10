from Utils.Utilities import powerset
from Utils import Configuration

fts = ['cat_start', 'cat_end', 'cat_speed_difference', 'type', 'traffic_lights', 'direction', 'incline']
lst = ['speed_change', 'type', 'traffic_lights', 'direction']
configurations = [list(x) for x in list(powerset(lst))]
for conf in configurations:
    if 'speed_change' in conf:
        conf.remove('speed_change')
        conf.extend(['cat_start', 'cat_end', 'cat_speed_difference'])

batch_name = "SupersegmentFeaturesGrid"
energy_config = Configuration.energy_config_superseg
energy_config['batch_dir'] = batch_name + "/"
energy_config['hidden_layers'] = 2
energy_config['cells_per_layer'] = 500
energy_config['features_used'] = [x for x in energy_config['features_used'] if x not in fts]
energy_config['iterations'] = 2
configs = []

for i in range(energy_config['iterations']):
    for f in configurations:
        conf = energy_config.copy()
        conf['features_used'] = conf['features_used'][:] + f
        conf['model_name_base'] = "SS_Energy_" + ("-".join(f) if len(f) > 0 else "None") + "No_Incline_Iter" + str(i+1)
        configs.append(conf)
