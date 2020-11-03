from astropy.convolution import convolve
import numpy as np
import scipy.stats


def get_enl_img(img: np.ndarray,
                window_size: int,
                enl_max: int = 20,
                mask: np.ndarray = None) -> np.ndarray:
    """
    This is the simplest way to to estimate the ENL i.e the Effective Number of
    Looks. Let E and V be the expected value and variance within a window
    determined by the `window_size`. Then enl computes the per-pixel ENL
    as E^2 / V.

    There are numerous related and more sophisticated methods discussed in
    Zhao's thesis [2].

    What's great is that astropy (used in this function) deals with np.nan
    values by interpolating across them on the fly quickly. This is extremely
    effective.

    Source:

    [1] https://github.com/WeiyingZhao/Multitemporal-SAR-image-denoising
    [2] https://www.theses.fr/2019SACLT003

    Parameters
    ----------
    img : np.ndarray
        The backscatter image. Assume that np.nan is nodata. If mask is
        specified additionally, then it generates a new image with nodata areas
        with values np.nan.
    window_size : int
        The `n x n` window. Must be odd (otherwise astropy)
        will throw an error.
    enl_max : int
        The maximum value allowed during binning.
        We clip the value after the computation.
    mask : np.ndarray
        The mask to ignore with True indicating areas to ignore.

    Returns
    -------
    np.ndarray:
        The ENL per-pixel image
    """
    if mask is not None:
        img_ = img.copy()
        img_[mask] = np.nan
    else:
        img_ = img

    kernel = np.ones((window_size, window_size))

    img_mean = convolve(img_,
                        kernel,
                        boundary='extend',
                        nan_treatment='interpolate',
                        normalize_kernel=True,
                        preserve_nan=True)
    img_sqr_mean = convolve(img_**2,
                            kernel,
                            normalize_kernel=True,
                            boundary='extend',
                            nan_treatment='interpolate',
                            preserve_nan=True)
    img_variance = img_sqr_mean - img_mean**2

    enl_img = img_mean**2 / np.clip(img_variance, .0001, 1./enl_max)
    enl_img = np.clip(enl_img, 0, enl_max)

    return enl_img


def get_enl_mode(enl_img: np.ndarray,
                 enl_min: int = 1,
                 enl_max: int = 20) -> float:
    """
    Put `enl_img` image into bins from enl_min, ... enl_max with intervals of
    .1 to find the maximum bin. Usually has one peak, but may wish to view the
    histogram.

    Parameters
    ----------
    enl_img : np.ndarray
        The image of per-pixel enl. Use the routine `get_enl_img`.
    enl_min : int
        The bottommost bin; must be greater than 1. Default is 1.
    enl_max : int
        The expected top most bin. Default is 20.

    Returns
    -------
    Float:
       The enl mode from the .1 bin.
    """
    if enl_min < 1:
        raise ValueError('enl_min must be > 1')

    data_ = enl_img[~np.isnan(enl_img)]

    int_max = int(np.ceil(data_.max()))
    data_max = min(int_max, enl_max)
    n_bins = (data_max - enl_min) * 10 + 1
    bins = np.linspace(enl_min, data_max, n_bins)

    result = scipy.stats.binned_statistic(data_,
                                          data_,
                                          statistic='count',
                                          bins=bins)
    counts = result.statistic
    return bins[np.argmax(counts)]


def get_enl_mask(img: np.ndarray,
                 db_min: float = -18,
                 additional_mask: np.ndarray = None) -> np.ndarray:
    """
    This is to generate a mask for ENL computations. Generally, ignore pixels
    within image (assumed to be linear scale) below db_min and additional_mask
    is one that can be included to further concentrate ENL estimates.

    Parameters
    ----------
    img : np.ndarray
        The linear-scale basckatter image to generate a mask from.
    db_min : float
        The db value to ignore pixels below this threshold.
    additional_mask : np.ndarray
        This is an additional mask in which True is nodata.

     Returns
    -------
    np.ndarray:
        The ENL mask with True = Nodata area and False = Data Areas.
    """
    nodata_mask = np.isnan(img)
    db_img = 10 * np.log10(img,
                           where=~nodata_mask,
                           out=np.ones(img.shape)*-9999
                           )
    system_noise_mask = (db_img < db_min)
    enl_mask = system_noise_mask | nodata_mask
    if additional_mask is not None:
        enl_mask = enl_mask | additional_mask
    return enl_mask
