import numpy as np
import scipy.ndimage as nd


def interpolate_nn(data: np.array) -> np.array:
    """
    Function to fill nan values in a 2D array using nearest neighbor
    interpolation.

    Source: https://stackoverflow.com/a/27745627

    Parameters
    ----------
    data : np.array
        Data array (2D) in which areas with np.nan will be filled in with
        nearest neighbor.

    Returns
    -------
    np.array:
        [TODO:description]
    """
    ind = nd.distance_transform_edt(np.isnan(data),
                                    return_distances=False,
                                    return_indices=True)
    return data[tuple(ind)]
