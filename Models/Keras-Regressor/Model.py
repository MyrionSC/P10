from keras import Sequential, initializers
from keras.layers import Dense, Dropout
from keras.utils import multi_gpu_model
from Metrics import rmse, r2
from keras.regularizers import l2


# Model definition for a simple linear regressor
def LinearRegressor(input_dim):
    model = Sequential()
    model.add(Dense(1, input_dim=input_dim, kernel_initializer='normal', activation='linear'))
    #model.add(Dense(1, kernel_initializer='normal'))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', 'mse', 'mape', rmse, r2])
    return model


def DNNRegressor(input_dim, output_dim, hidden_layers, cells_per_layer, activation, kernel_initializer, optimizer, initial_dropout, dropout):
    # Some sources say that with ReLU activations, the biases should not be zero initialized.
    # This is because it can result in "dead neurons".

    model = Sequential()

    # Adds input layer and first hidden layer
    model.add(Dense(cells_per_layer, input_dim=input_dim, kernel_initializer=kernel_initializer, bias_initializer=initializers.Constant(0.1), activation=activation))
    if initial_dropout > 0:
        model.add(Dropout(initial_dropout))

    # Adds k-1 hidden layers
    for i in range(hidden_layers - 1):
        model.add(Dense(cells_per_layer, kernel_initializer=kernel_initializer, bias_initializer=initializers.Constant(0.1), activation=activation))
        if dropout > 0:
            model.add(Dropout(dropout))

    model.add(Dense(output_dim, kernel_initializer='normal'))

    # Uncomment this line for multi-GPU support
    # model = multi_gpu_model(model, gpus=2)

    model.compile(loss='mape', optimizer=optimizer, metrics=['mae', 'mse', 'mape', rmse])
    return model
