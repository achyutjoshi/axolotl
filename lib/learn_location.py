from axolotl import *
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from keras import backend as K
import numpy as np

# config
print_predictions = True
graph_predictions = True
graph_error_dist = True

IPHONE_HEIGHT = 1920. / 401 # 1920px at 401ppi per https://www.apple.com/iphone-7/specs/
IPHONE_WIDTH = 1080. / 401 # 1080px at 401ppi

def in_distance(y_true, y_pred):
    y_error = y_true - y_pred
    y_error_normalized = (y_error) / 2 # the width is currently 2 (as the coordinates are [-1, 1])
    y_scaled_error = K.dot(y_error_normalized, K.constant(np.array([[IPHONE_WIDTH, 0], [0, IPHONE_HEIGHT]])))
    y_distance_sq = K.sum(K.square(y_scaled_error), axis=-1)
    y_distance = K.sqrt(y_distance_sq)
    return y_distance

def in_dist_mean(*args, **kwargs):
    return K.mean(in_distance(*args, **kwargs))

def train_location_model(data):
    # find windows where touching
    touching_windows, touching_labels = get_touching_windows(data, with_labels=True)
    expanded_touching_windows = expand_windows_interpolated(data, touching_windows)
    # convert to feature vectors
    positive_feature_vectors = feature_vectors_from_windows(expanded_touching_windows)
    # split into input (X) and output (Y) variables
    X = np.array(map(np.array, positive_feature_vectors))
    Y = np.array(map(np.array, touching_labels))
    # create model
    model = Sequential()
    model.add(Dense(window_samples * 4, input_dim=window_samples * 6, activation='linear'))
    model.add(Dense(window_samples * 2, activation='linear'))
    model.add(Dense(window_samples, activation='linear'))
    model.add(Dense(2, activation='linear'))
    # Compile model
    model.compile(loss='mse', optimizer='adam', metrics=['mse', in_dist_mean])
    # Fit the model
    model.fit(X, Y, nb_epoch=40, batch_size=20, verbose=0)
    return model

def learn_location(accel_file, gyro_file, verbose=True):
    # read the data in
    data = read_data(accel_file, gyro_file)

    # find windows where touching
    touching_windows, touching_labels = get_touching_windows(data, with_labels=True)
    expanded_touching_windows = expand_windows_interpolated(data, touching_windows)

    # convert to feature vectors
    positive_feature_vectors = feature_vectors_from_windows(expanded_touching_windows)

    # learn

    # fix random seed for reproducibility
    # seed = 12
    # np.random.seed(seed)

    # split into input (X) and output (Y) variables
    X = np.array(map(np.array, positive_feature_vectors))
    Y = np.array(map(np.array, touching_labels))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33)

    # create model
    model = Sequential()
    model.add(Dense(window_samples * 4, input_dim=window_samples * 6, activation='linear'))
    model.add(Dense(window_samples * 2, activation='linear'))
    model.add(Dense(window_samples, activation='linear'))
    model.add(Dense(2, activation='linear'))

    # Compile model
    model.compile(loss='mse', optimizer='adam', metrics=['mse', in_dist_mean])

    # Fit the model
    verbosity = 0
    if verbose:
        verbosity = 1
    model.fit(X_train, Y_train, validation_data=(X_test, Y_test), nb_epoch=40, batch_size=20, verbose=verbosity)

    # print predictions
    if print_predictions and verbose:
        for x_val, y_val in zip(X_test, Y_test):
            print y_val, ":", model.predict(np.array([x_val]), verbose=0)

    # Show histogram of data
    if graph_error_dist:
        pred = model.predict(X_test)
        plt.hist(K.eval(in_distance(K.constant(Y_test), K.constant(pred))), bins=20, normed=True)
        plt.show()

    # graph predictions
    if graph_predictions and verbose:
        m = 10
        n = 10

        pred_data = zip(X_test, Y_test)

        for ii in xrange(min(m * n, len(X))):
            x_val, y_val = pred_data[ii]

            curr_plot = plt.subplot(m, n, ii + 1) # the position parameter is 1-indexed

            plt.plot(y_val[0], y_val[1], 'go')
            pred = model.predict(np.array([x_val]), verbose=0).flatten()
            plt.plot(pred[0], pred[1], 'ro')

            curr_plot.xaxis.set_visible(False)
            curr_plot.yaxis.set_visible(False)

            plt.ylim(-1, 1)
            plt.xlim(-1, 1)

        plt.show()

    return dict(zip(model.metrics_names, model.evaluate(X_test, Y_test, verbose=verbosity)))

if __name__ == "__main__":
    learn_location("data/sample_0/accel.txt", "data/sample_0/gyro.txt")
    print ""
