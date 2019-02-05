from Utils import save_model, read_data
from Model import DNNRegressor
from config import paths, config, def_features
from tensorflow import set_random_seed
from numpy.random import seed
from sklearn.metrics import r2_score
import time
import json
import os

seed(1337)  # Numpy seed
set_random_seed(1337)  # TensorFlow seed

history_collection = list()

print(config['embedding_path'] + "  -  Removed features: " + ', '.join(config['remove_features']))
X_train, Y_train, num_features, num_labels, embeddings_used, trip_ids_train \
    = read_data(paths['trainPath'], config['target_feature'], config['remove_features'], scale=True)
X_validation, Y_validation, _, _, _, trip_ids_validation \
    = read_data(paths['validationPath'], config['target_feature'], config['remove_features'], scale=True)

# Create estimator
estimator = DNNRegressor(num_features, num_labels, config['hidden_layers'], config['cells_per_layer'],
                         config['activation'], config['kernel_initializer'], config['optimizer'], config['initial_dropout'], config['dropout'])

print("Starting training of DNN")
start_time = time.time()
# Train estimator and get training history
history = estimator.fit(X_train, Y_train, epochs=config['epochs'], validation_data=(X_validation, Y_validation),
                        batch_size=config['batch_size'], verbose=1, shuffle=True)
end_time = time.time()
print('Time to complete %s epochs: %s seconds with batch size %s' % (config['epochs'], end_time - start_time, config['batch_size']))

# Define new parameter dictionary without iterations (this means only one model is saved)
param_string = ','.join("%s=%s" % (key, config[key]) for key in def_features)
embeddings_used_string = ""
if len(embeddings_used) > 0:
    embeddings_used_string = " - " + ','.join("%s" % x for x in embeddings_used)

# Save estimator
model_output_path = ("saved_models/DNNRegressor")# %s%s - %s" % (config['target_feature'], embeddings_used_string, param_string))
save_model(estimator, model_output_path)
history_collection.append((config.copy(), history.history))
print()

prediction = estimator.predict(X_train, batch_size=config['batch_size'], verbose=1)
val_prediction = estimator.predict(X_validation, batch_size=config['batch_size'], verbose=1)
train_r2 = r2_score(Y_train, prediction)
val_r2 = r2_score(Y_validation, val_prediction)
history.history['train_r2'] = train_r2
history.history['val_r2'] = val_r2

# Save history
history_output_path = ("saved_history/Predicting DNNRegressor")#%s%s - %s.json" % (config['target_feature'], embeddings_used_string, param_string))
if os.path.isdir("saved_history") and os.path.isfile(history_output_path):
    with open(history_output_path) as f:
        history_list = json.load(f)
else:
    history_list = list()

history_list.append(history.history)
history_json = json.dumps(history_list)

if not os.path.isdir("saved_history"):
    os.makedirs(os.path.dirname(history_output_path))
with open(history_output_path, "w") as f:
    f.write(history_json)

for config, results in history_collection:
    print(config)
    print(print(config['embedding_path'] + "  -  Removed features: " + ', '.join(config['remove_features'])))
    print("Train R2: {:f}".format(results['train_r2']) + "  -  Validation R2: {:f}".format(results['val_r2']))