import numpy as np
import scipy.ndimage as nd


def interpolate_nn(data: np.array) -> np.array:
    """Function to fill nan values in a 2D array using nearest neighbor
    interpolation.

    Arguments:
        data (array): A 2D array containing the data to fill.  Void elements
            should have values of np.nan.

    Returns:
        filled (array): The filled data.

    """
    ind = nd.distance_transform_edt(np.isnan(data), return_distances=False, return_indices=True)
    return data[tuple(ind)]
