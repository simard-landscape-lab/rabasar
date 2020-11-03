import numpy as np


def scale_img(img: np.ndarray,
              new_min: int = 0,
              new_max: int = 1) -> np.ndarray:
    """
    Scale an image by the absolute max and min in the array to have dynamic
    range new_min to new_max. Useful for visualization.

    Parameters
    ----------
    img : np.ndarray
    new_min : int
    new_max : int

    Returns
    -------
    np.ndarray:
       New image with shape equal to img, scaled to [new_min, new_max]
    """
    i_min = np.nanmin(img)
    i_max = np.nanmax(img)
    if i_min == i_max:
        # then image is constant image and clip between new_min and new_max
        return np.clip(img, new_min, new_max)
    img_scaled = (img - i_min) / (i_max - i_min) * (new_max - new_min)
    img_scaled += new_min
    return img_scaled
