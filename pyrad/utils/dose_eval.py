from typing import Union

import numpy as np
import pymedphys
import SimpleITK as sitk
from pyrad.utils import image_utils


def calculate_gamma(dose1: sitk.Image, dose2: sitk.Image, params):
    assert isinstance(dose1, sitk.Image)
    reference = dose1

    # Get physical coordinates for x, y and z axes.
    x = np.array([dose1.TransformIndexToPhysicalPoint((idx, 0, 0))[0] \
                                        for idx in range(dose1.GetSize()[0])])
    
    y = np.array([dose1.TransformIndexToPhysicalPoint((0, idx, 0))[1] \
                                        for idx in range(dose1.GetSize()[1])])
    
    z = np.array([dose1.TransformIndexToPhysicalPoint((0, 0, idx))[2] \
                                        for idx in range(dose1.GetSize()[2])])

    coords = (z, y, x)
    dose1 = sitk.GetArrayFromImage(dose1)
    dose2 = sitk.GetArrayFromImage(dose2)

    # Pymedphys gamma implementation: https://docs.pymedphys.com/lib/ref/gamma.html
    gamma_map = pymedphys.gamma(coords, dose1, coords, dose2,
                            **params)

    # nan values found in locations where the beam does not apply any dose
    valid_gamma = gamma_map[~np.isnan(gamma_map)]

    passing_rate = 100 * np.round(np.sum(valid_gamma <= 1) / len(valid_gamma), 6)

    gamma_map = sitk.GetImageFromArray(gamma_map)
    gamma_map.CopyInformation(reference)
    
    return gamma_map, passing_rate


def calculate_dose_diff(dose1: sitk.Image, dose2: sitk.Image):
    return dose1 - dose2
