""" Helper functions for matrix factorization analysis
"""
import numpy as np
from brainiak.funcalign.srm import SRM
from sklearn.decomposition import PCA


def fit_srm(n_components, data_train, data_test):
    """Fit the shared response model
    Parameters
    ----------
    n_components: k
    data_train: 3d array (n_subj, n_features, n_examples/tps)
    data_test: 3d array (n_subj, n_features, n_examples/tps)

    Returns
    -------
    data_train_shared: 3d array (n_subj, n_components, n_examples/tps)
        the transformed training set
    data_test_shared: 3d array (n_subj, n_components, n_examples/tps)
        the transformed test set
    srm: the fitted model
    """
    #
    srm = SRM(features=n_components)
    # fit SRM on the training set
    data_train_shared = srm.fit_transform(data_train)
    # transform the hidden activity (on the test set) to the shared space
    data_test_shared = srm.transform(data_test)
    return data_train_shared, data_test_shared, srm


def trace_var_exp_srm(n_component_list, Xs_train, Xs_test):
    """Trace the test set variance explained curve (but don't double dip!)
        over the number of components
    """
    n_subjects = len(Xs_train)
    # get the total variance for each subject
    Xs = [np.hstack([Xs_train[s], Xs_test[s]]) for s in range(n_subjects)]
    subj_var = [np.var(X) for X in Xs]
    # compute the variance explained
    srm_var_exp = np.zeros(len(n_component_list))
    for i in range(len(n_component_list)):
        # fit SRM
        _, Xs_test_shared, srm_model = fit_srm(
            n_component_list[i], Xs_train, Xs_test)
        # transform back to native space, then check reconstruction error
        reconstructed = [np.dot(srm_model.w_[k], Xs_test_shared[k])
                         for k in range(n_subjects)]
        # compute variance explained
        srm_var_exp[i] = 1-np.mean([
            np.square(reconstructed[k]-Xs_test[k]).mean()/subj_var[k]
            for k in range(n_subjects)
        ])
    return srm_var_exp


def procrustes_align(X_new, S_target):
    """One-step deterministic SRM
    Parameters
    ----------
    X_new:
        an activation trajectory
    S_target:
        pre-computed shared response as the alignment target

    Returns
    -------
    W:
        the transformation matrix from X to S
    X_aligned:
        the aligned trajectory
    """
    U, s_vals, VT = np.linalg.svd(X_new @ S_target.T, full_matrices=False)
    W = U @ VT
    X_aligned = W.T @ X_new
    return W, X_aligned


def fit_pca(n_components, data_train, data_test):
    """Fit PCA
    Parameters
    ----------
    n_components: k
    data_train: 2d array (n_features, n_examples/tps)
    data_test: 2d array (n_features, n_examples/tps)

    Returns
    -------
    data_train_pca: 3d array (n_subj, n_components, n_examples/tps)
        the transformed training set
    data_test_pca: 3d array (n_components, n_examples/tps)
        the transformed test set
    pca: the fitted model
    """
    pca = PCA(n_components=n_components)
    # tranpose the data to make the format consistent with SRM fit
    data_train_pca = pca.fit_transform(data_train.T).T
    data_test_pca = pca.transform(data_test.T).T
    return data_train_pca, data_test_pca, pca


def fit_pca_thresholded(n_components, var_exp_threshold, data_train, data_test):
    """Fit PCA
    Parameters
    ----------
    n_components: k
    var_exp_threshold: float \in (0,1)
        the amount of variance you wanna explain
    data_train: 2d array (n_features, n_examples/tps)
    data_test: 2d array (n_features, n_examples/tps)

    Returns
    -------
    data_train_pca: 3d array (n_subj, n_components, n_examples/tps)
        the transformed training set
    data_test_pca: 3d array (n_components, n_examples/tps)
        the transformed test set
    pca: the fitted model
    """
    # fit PCA with the input number of components
    _, _, pca_model = fit_pca(n_components, data_train, data_test)
    # compute prop variance explained by the 1st k components
    cum_var_exp = np.cumsum(pca_model.explained_variance_ratio_)
    # find k, s.t. PCA(k) explain more variance than the threshold
    candidiates_components = np.where(cum_var_exp > var_exp_threshold)[0]
    # choose k = 1st candidate or the input components
    if len(candidiates_components) == 0:
        n_components_threshold = n_components
    else:
        n_components_threshold = candidiates_components[0]
    # re-fit PCA
    data_train_pca, data_test_pca, final_pca_model = fit_pca(
        n_components_threshold, data_train, data_test)
    return data_train_pca, data_test_pca, final_pca_model


"""utils
"""


def chose_n_components(n_component_list, cum_var_exp, var_exp_threshold):
    assert len(n_component_list) == len(cum_var_exp)
    assert var_exp_threshold > 0 and var_exp_threshold < 1
    # find k, s.t. PCA(k) explain more variance than the threshold
    candidiates_ids = np.where(cum_var_exp > var_exp_threshold)[0]
    # choose k = 1st candidate or the input components
    if len(candidiates_ids) == 0:
        best_n_component = n_component_list[-1]
    else:
        best_n_component = n_component_list[candidiates_ids[0]]
    return best_n_component
