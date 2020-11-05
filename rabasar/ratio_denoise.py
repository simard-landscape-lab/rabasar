from skimage.restoration import denoise_tv_bregman
import numpy as np
from numpy.linalg import norm
import scipy
from tqdm import tqdm
import bm3d


def admm_ratio_denoise(img: np.ndarray,
                       L: float,
                       Lm: float,
                       regularizer: str,
                       regularizer_params: dict = None,
                       max_admm_iterations: int = 10,
                       newton_iterations: int = 3,
                       denoiser_iterations: int = 10,
                       x_init: np.ndarray = None,
                       convergence_crit: float = 1e-5) -> np.ndarray:
    """
    We use the variables using Boyd's ADMM review article in [1].

    This is essentially the same implementation as the `admm_spatial_denoise`
    in `spatial_denoise.py` save for the likelihood function used for the noise
    model as noted in the Rabasar paper [2] and some initialization. It may be
    good to combine them using the common implementations, but for clarity we
    leave them separat.

    [1] https://stanford.edu/~boyd/papers/pdf/admm_distr_stats.pdf
    [2] https://hal.archives-ouvertes.fr/hal-01791355v2

    Parameters
    ----------
    img : np.ndarray
        The ratio image. The image is I / I_ta, where I is the image in the
        time series and I_ta is the temporally averaged reference.
    L : float
        This is the ENL for img in the numerator.
    Lm: float
        This is the ENL of the temporally averaged reference image in the
        denominator of the ratio.
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

    eta = 0.95
    gamma = 1.05
    block_diff = block_diff_old = np.inf
    block_diff_list = []

    # Log
    img_db = np.log10(img)

    # see:
    # https://github.com/WeiyingZhao/Multitemporal-SAR-image-denoising/blob/master/rulog.m#L114
    # the original paper references pg. 4 of Mulog paper.
    var = float(scipy.special.polygamma(1, L))
    beta = (1 + 2/L + 2/Lm) / var

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

    if x_init is None:
        x_k = img_db.copy()
    else:
        x_k = x_init.copy()
    z_k = denoiser(x_k, lamb_param)
    u_k = z_k - x_k

    for k in tqdm(range(max_admm_iterations), desc='admm_iterations'):

        z_kp1 = denoiser(x_k - u_k, (lamb_param * beta))
        u_kp1 = u_k + z_kp1 - x_k

        x_kp1 = x_k.copy()
        for i in range(newton_iterations):
            x_kp1 = ratio_lklhd_iter(x_kp1, z_kp1 + u_kp1, img_db, L, Lm, beta)

        # Not sure about this, but plug and play?
        block_diff = (norm(x_k - x_kp1) +
                      norm(u_k - u_kp1) +
                      norm(z_k - z_kp1)
                      )
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


def ratio_lklhd_iter(x_k, a_k, img, L, Lm, beta):
    exp_diff = np.exp(img - x_k)
    c = (Lm + L) * exp_diff / (Lm + L * exp_diff)
    numer = beta * (x_k - a_k) + L * (1 - c)
    denom = beta + L * c * (1 - L / (Lm + L) * c)
    x_kp1 = x_k - numer / denom
    return x_kp1
