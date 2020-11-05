from skimage.restoration import denoise_tv_bregman
import numpy as np
from numpy.linalg import norm
import scipy
from tqdm import tqdm
import bm3d


def midal_denoise(img: np.array,
                  L: float,
                  regularizer: str,
                  regularizer_params: dict = None,
                  max_admm_iterations: int = 10,
                  newton_iterations: int = 3,
                  denoiser_iterations: int = 10,
                  convergence_crit: float = 1e-5) -> np.array:
    """
    This is an implementation of the variational approach discussed in [1].
    There are currently only two supported regularizers:
        + total-variation (`tv`)
        + bm3d (`bm3d`)

    The total variation regularizer is equivalent to the method discussed in
    [2]. The general framework for the optimization procedure below is:

    $$
    X_d = argmin_{X}  R(X) + lamb cdot P(X | X_0)
    $$

    where $X_0$ is the original image and $X_d$ is the final despeckled image.
    The implementation uses the TV method from [3] so that is why the
    regularization parameter is placed where it is. Technically, the weight
    parameter is 2 * lamb (using the original implementation's model). However,
    this is all selected heurisitically and so it's not so important.

    [1] https://arxiv.org/abs/1704.05335
    [2] https://arxiv.org/pdf/0912.1845.pdf
    [3]
    https://scikit-image.org/docs/0.17.x/api/skimage.restoration.html#denoise-tv-bregman

    Parameters
    ----------
    img : np.ndarray
        The original image
    L : float
        This is the ENL for img.
    regularizer : str
        The string identifier for the regularizer. The accepted values are `tv`
        and `bm3d`.
    regularizer_params : dict
        For `tv`:
            + {
                'weight': float
              }
        For `bm3d`:
            + {
                'weight`: float
              }
    max_admm_iterations : int
        The maximum number of iterations. Default = 10.
    newton_iterations : int
        Maximum number of newton iterations per ADMM loop. Default = 3.
    denoiser_iterations : int
        The number of denoiser iterations (if applicable). Default = 10.
    convergence_crit : float
        The value for the sum of the residuals to be smaller than and to stop
        ADMM. Default = 1e-5

    Returns
    -------
    np.array:
       Denoised Image
    """

    if regularizer not in ['tv', 'bm3d']:
        raise NotImplementedError('''Only bm3d and tv (using split-bregman)
                                     is implemented''')

    # Parameters
    # Selected as in
    # https://bitbucket.org/charles_deledalle/mulog/src/8a1172795c1ed598e4c7d1fe989876774fbded64/mulog/admm.m#lines-127:129
    # They reference the Plug-and-Play paper by Chan et al.
    eta = 0.95
    gamma = 1.05

    block_diff = block_diff_old = np.inf
    block_diff_list = []

    # Log Image
    img_db = np.log10(img)

    # see mulog pg. 4
    # Compute the variance according to the noise model
    # And then initialize beta as suggested.
    var = float(scipy.special.polygamma(1, L))
    beta = (1 + 2/L) / var

    ################
    # Denoiser Setup
    ################

    if regularizer == 'tv':
        lamb_param = regularizer_params['weight']
        isotropic = regularizer_params.get('isotropic', True)

        def denoiser(X, lamb):
            return denoise_tv_bregman(X,
                                      lamb,
                                      max_iter=denoiser_iterations,
                                      isotropic=isotropic)
    elif regularizer == 'bm3d':
        lamb_param = regularizer_params['weight']

        def denoiser(X, lamb):
            return bm3d.bm3d(X, lamb)
    else:
        pass

    ###############################
    # Begin Plug and Play ADMM Loop
    ###############################

    x_k = img_db.copy()
    z_k = denoiser(x_k, lamb_param)
    u_k = z_k - x_k

    for k in tqdm(range(max_admm_iterations), desc='admm_iterations'):

        z_kp1 = denoiser(x_k - u_k, (lamb_param * beta))
        u_kp1 = u_k + z_kp1 - x_k
        x_kp1 = x_k.copy()
        for i in range(newton_iterations):
            x_kp1 = newton_lklhd_iter(x_kp1, z_kp1 + u_kp1, img_db, L, beta)

        block_diff = norm(x_k - x_kp1) + norm(u_k - u_kp1) + norm(z_k - z_kp1)
        if block_diff > eta * block_diff_old:
            beta = gamma * beta
        z_k = z_kp1
        u_k = u_kp1
        x_k = x_kp1
        block_diff_old = block_diff
        block_diff_list.append(block_diff)
        if block_diff < convergence_crit:
            break

    return np.power(10, x_k), block_diff_list


def newton_lklhd_iter(x_k: np.array,
                      a_k: np.array,
                      img: np.array,
                      L: float,
                      beta: float) -> np.array:
    numer = beta * (x_k - a_k) + L * (1 - np.exp(img - x_k))
    denom = beta + L * np.exp(img - x_k)
    x_kp1 = x_k - numer / denom
    return x_kp1
