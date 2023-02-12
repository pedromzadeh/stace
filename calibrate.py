import numpy as np
import pandas as pd


def correct_values(x, measured_endpoints, truth_endpoints):
    """
    Calibrates (corrects) a set of sensor readings by matching the endpoints
    measured by the sensor to the truth value of the endpoints.

    Note
    ----
    Endpoints depend on the sensor type. A temperature sensor will have ice and
    boil baths as its endpoints for example.

    Parameters
    ----------
    x : array_like of shape (n_samples, )
        The sensor recordings to be calibrated.

    measured_endpoints : list of shape (2, )
        Values measured by this sensor for each of two endpoints,
        with ordering being (low, high).

    truth_endpoints : list of shape (2, )
        Truth values of each of two endpoints, with ordering being
        (low, high).

    Returns
    -------
    np.ndarray
    """
    y1, y2 = measured_endpoints
    Y1, Y2 = truth_endpoints
    slope = (Y2 - Y1) / (y2 - y1)

    if isinstance(x, pd.DataFrame):
        x = x.values()
    if isinstance(x, list):
        x = np.array(x)

    return slope * (x - y1) + Y1
