import numpy as np


def reflect_upper_triangular_part(matrix):
    """Copy the lower triangular part to the upper triangular part
        This speed up RSA computation
    Parameters
    ----------
    matrix: a 2d array

    Returns
    -------
    matrix with upper triangular part filled
    """
    irows, icols = np.triu_indices(np.shape(matrix)[0], 1)
    matrix[irows, icols] = matrix[icols, irows]
    return matrix


def window_avg(matrix, win_size):
    """ non-overlapping window averaging, over axis 0
    """
    n0, n1 = np.shape(matrix)
    n0_new = n0 // win_size
    # preallocate
    matrix_avg = np.zeros((n0_new, n1))
    # compute the average within each non-overlapping window
    for i in range(n0_new):
        idx_start = i * win_size
        idx_end = (i + 1) * win_size
        matrix_avg[i, :] = np.mean(matrix[idx_start: idx_end, :], axis=0)
    return matrix_avg


"""helper functions"""


def print_dict(input_dict):
    for key, val in input_dict.items():
        print('%s: %s', key, val)


def print_list(input_list):
    for item in input_list:
        print('%s' % item)


# """demo"""
#
# import numpy as np
# import matplotlib.pyplot as plt
#
# # make a sine wave with noise
# times = np.arange(0, 10*np.pi, .01)
# X = np.vstack([np.sin(times), np.cos(times)])
#
# # smoothing it with a running average in one line using a convolution
# #    using a convolution, you could also easily smooth with other filters
# #    like a Gaussian, etc.
# win_size = 1000
# smoothed = np.convolve(wfm, np.ones(win_size)/win_size, mode='same')
#
# plt.plot(times, wfm)
# plt.plot(times, smoothed)
#
#
# X_avgd = moving_window_avg(X.T, 0, win_size)
# np.shape(X.T)
# np.shape(X_avgd)
# plt.plot(X.T, color='blue')
# plt.plot(X.T, color='blue')
