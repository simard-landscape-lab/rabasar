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

    eta = 0.95
    gamma = 1.05
    block_diff = block_diff_old = np.inf
    block_diff_list = []

    # Log
    img_db = np.log10(img)

    # see mulog pg. 4
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
