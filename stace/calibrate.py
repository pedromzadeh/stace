import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

class Calibrate(ABC):
    """
    Base calibration class defining the blueprint for different types
    of calibration classes.
    """
    @abstractmethod
    def correct(self, X):
        pass


class OnePoint(Calibrate):
    """
    Defines a one-point calibration object.
    """

    def __init__(self, measured, reference):
        """
        Initializes the object.

        Parameters
        ----------
        measured : float
            Specifies the sensor measurement for the reference point.

        reference : float
            Specifies the truth value for the reference point.
        """
        self.measured = measured
        self.reference = reference

    def correct(self, X):
        """
        Corrects the input measured values.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, )
            Raw sensor readings to be corrected.

        Returns
        -------
        np.ndarray of shape (n_samples, )
            Corrected values.
        """
        offset = self.reference - self.measured
        return X + offset


class TwoPoint(Calibrate):
    """
    Defines a two-point calibration object.
    """

    def __init__(self, ref_pts):
        """
        Initializes the object.

        Parameters
        ----------
        ref_pts : list of tuples of shape (2, 2)
            Specifies the two reference points being used. The format for each
            reference point is (sensor measurement, truth value).
        """
        self.x1, self.y1 = ref_pts[0]
        self.x2, self.y2 = ref_pts[1]
    
    def correct(self, X):
        """
        Corrects the input measured values.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, )
            Raw sensor readings to be corrected.

        Returns
        -------
        np.ndarray of shape (n_samples, )
            Corrected values.
        """
        return (y2 - y1) / (x2 - x1) * (X - x1) + y1


class ThreePoint(Calibrate):
    """
    Defines a three-point calibration object.
    """

    def __init__(self, ref_pts):
        """
        Initializes the object.

        Parameters
        ----------
        ref_pts : list of tuples of shape (3, 2)
            Specifies the three reference points being used. The format for each
            reference point is (sensor measurement, truth value).
        """
        self.x1, self.y1 = ref_pts[0]
        self.x2, self.y2 = ref_pts[1]
        self.x3, self.y3 = ref_pts[2]
        self.coeffs = self._coeffs()

    def correct(self, X):
        """
        Corrects the input measured values.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, )
            Raw sensor readings to be corrected.

        Returns
        -------
        np.ndarray of shape (n_samples, )
            Corrected values.
        """
        coeffs = self.coeffs
        return coeffs[0] + coeffs[1] * X + coeffs[2] * X**2

    def _coeffs(self):
        x1, x2, x3 = self.x1, self.x2, self.x3
        y1, y2, y3 = self.y1, self.y2, self.y3
        Y = np.array([y1, y2, y3]).reshape(-1, 1)
        X = np.array([[1, x1, x1**2], [1, x2, x2**2], [1, x3, x3**2]])
        return np.linalg.inv(X).dot(Y).reshape(-1)


