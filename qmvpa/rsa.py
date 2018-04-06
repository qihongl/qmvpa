"""Functions for Representational Similarity Analysis
"""

import numpy as np
from scipy.spatial import procrustes
from qmvpa.utils import reflect_upper_triangular_part


def within_RSMs(Xs):
    """Compute all within-subject RSMs
    Parameters
    ----------
    Xs: a list of 2d array in the form of (n_feature_dim x n_examples)
        the activation matrices

    Returns
    -------
    rsms
        a list of representational similarity matrices
    """
    # compute RSM
    num_subjects = len(Xs)
    rsms = [inter_RSM(Xs[s], Xs[s]) for s in range(num_subjects)]
    return rsms


def correlate_2RSMs(rsm1, rsm2):
    """Compute the correlation between 2 RSMs (2nd order correlations)
    Parameters
    ----------
    rsm_i: a 2d array in the form of (n_examples x n_examples)
        a representational similarity matrix

    Returns
    -------
    r: float
        linear_correlation(rsm1, rsm2)
    """
    # compute the linear correlation of 2 vectorized RSMs
    r = np.corrcoef(np.reshape(rsm1, (-1,)), np.reshape(rsm2, (-1,)))[0, 1]
    return r


def correlate_RSMs(rsms):
    """Compute correlation between RSMs (2nd order correlations)
    Parameters
    ----------
    rsms: a list of 2d array in the form of (n_examples x n_examples)
        representational similarity matrces

    Returns
    -------
    rsm_corrs: 2d array in the form of (num_rsms x num_rsms)
    """
    num_subjects = len(rsms)
    rsm_corrs = np.zeros((num_subjects, num_subjects))
    for i in range(num_subjects):
        for j in np.arange(0, i+1, 1):
            rsm_corrs[i, j] = correlate_2RSMs(
                rsms[i], rsms[j])
    # fillin the upper triangular part by symmetry
    rsm_corrs = reflect_upper_triangular_part(rsm_corrs)
    return rsm_corrs


def inter_RSM(m1, m2):
    """Compute the RSM for 2 activation matrices
    Parameters
    ----------
    mi: 2d array (n_feature_dim x n_examples)
        a activation matrix

    Returns
    -------
    intersubj_rsm
        corr(col_i(m1), col_j(m2)), for all i and j
    """
    assert np.shape(m1) == np.shape(m2)
    n_examples = np.shape(m1)[1]
    intersubj_rsm = np.corrcoef(m1.T, m2.T)[:n_examples, n_examples:]
    # assert(np.shape(m1)[1] == np.shape(m2)[1])
    # n_examples = np.shape(m1)[1]
    # # compute the correlation matrix of hidden activity
    # intersubj_rsm = np.zeros((n_examples, n_examples)
    # for i in range(n_examples):
    #     for j in np.arange(0, i+1, 1):
    #         intersubj_rsm[i, j] = np.corrcoef(m1[:, i], m2[:, j])[0, 1]
    #         if all(m1[:, i] == 0) or all(m2[:, j] == 0):
    #             intersubj_rsm[i, j] = 0
    # # fillin the upper triangular part by symmetry
    # intersubj_rsm = reflect_upper_triangular_part(intersubj_rsm)
    return intersubj_rsm


def inter_RSMs(matrix_list):
    """Compute intersubject representational similarity for a list of acts
        when comparing (k-1) subjects to left-out subject, average the k

    Parameters
    ----------
    matrix_list: a list of 2d array in the form of (n_feature_dim x n_examples)
        the activation matrices

    Returns
    -------
    intersubj_rsm
        the average intersubject representational similarity matrix
    """
    matrix_array = np.array(matrix_list)
    len(matrix_list)
    intersubj_rsms = []
    for loo_idx in range(len(matrix_list)):
        mean_Hs = np.mean(
            matrix_array[np.arange(len(matrix_list)) != loo_idx], axis=0)
        intersubj_rsms.append(inter_RSM(matrix_array[loo_idx], mean_Hs))
    intersubj_rsm = np.mean(intersubj_rsms, axis=0)
    return intersubj_rsm


def inter_procrustes(matrix_array):
    # input: matrix_array, n_subj x n_units x n_examples
    n_nets = np.shape(matrix_array)[0]
    D = np.zeros((n_nets, n_nets))
    for i in range(n_nets):
        for j in np.arange(0, i):
            _, _, D[i, j] = procrustes(matrix_array[i], matrix_array[j])
    return D
