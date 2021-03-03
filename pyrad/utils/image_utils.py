import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import SimpleITK as sitk
from pathlib import Path

# https://github.com/SimpleITK/SlicerSimpleFilters/blob/master/SimpleFilters/SimpleFilters.py
SITK_INTERPOLATOR_DICT = {
    'nearest': sitk.sitkNearestNeighbor,
    'linear': sitk.sitkLinear,
    'gaussian': sitk.sitkGaussian,
    'label_gaussian': sitk.sitkLabelGaussian,
    'bspline': sitk.sitkBSpline,
    'hamming_sinc': sitk.sitkHammingWindowedSinc,
    'cosine_windowed_sinc': sitk.sitkCosineWindowedSinc,
    'welch_windowed_sinc': sitk.sitkWelchWindowedSinc,
    'lanczos_windowed_sinc': sitk.sitkLanczosWindowedSinc
}


def plot_dose_diff(dose_diff, limit=(-0.2, 0.2)):
    # If 3 dimensional dose map, take only mid slice
    if dose_diff.ndim == 3:
        dose_diff = dose_diff[dose_diff.shape[0] // 2]

    plt.imshow(dose_diff, clim=limit, cmap='seismic')
    plt.colorbar()
    plt.show()


def save_dose_diff(dose_diff: Union[sitk.Image, np.array], label='diff', dir='.', limit=(-0.2, 0.2)):
    if isinstance(dose_diff, sitk.Image):
        dose_diff = sitk.GetArrayFromImage(dose_diff)

    dir = Path(dir).resolve()
    # If 3 dimensional dose map, take only mid slice
    if dose_diff.ndim == 3:
        dose_diff = dose_diff[dose_diff.shape[0] // 2]

    fig = plt.figure()
    plt.imshow(dose_diff, clim=limit, cmap='seismic')
    plt.title(label)
    plt.colorbar()
    plt.savefig(dir / f"{label}.png")


def save_gamma(gamma: Union[sitk.Image, np.array], label='gamma', dir='.', limit=(0, 2)):
    if isinstance(gamma, sitk.Image):
        gamma = sitk.GetArrayFromImage(gamma)

    dir = Path(dir).resolve()
    # If 3 dimensional dose map, take only mid slice
    if gamma.ndim == 3:
        gamma = gamma[gamma.shape[0] // 2]

    fig = plt.figure()
    plt.imshow(gamma, clim=limit, cmap='coolwarm')
    plt.title(label)
    plt.colorbar()
    plt.savefig(dir / f"{label}.png")


def np_to_sitk(array, ref_image=None):
    image = sitk.GetImageFromArray(array)

    if ref_image is not None:
        image.CopyInformation(ref_image)

    return image


def get_abs_value_stats(image: sitk.Image):
    abs_filter = sitk.AbsImageFilter()
    image = abs_filter.Execute(image)
    stats_filter = sitk.StatisticsImageFilter()
    stats_filter.Execute(image)
    return {
        'mean': stats_filter.GetMean(),
        'std': stats_filter.GetSigma(),
        'max': stats_filter.GetMaximum(),
        'min': stats_filter.GetMinimum()
    }


def resample_image_to_spacing(image,
                              new_spacing,
                              default_value,
                              interpolator='linear'):
    """Resample an image to a new spacing.
    """
    assert interpolator in SITK_INTERPOLATOR_DICT, \
        (f"Interpolator '{interpolator}' not part of SimpleITK. "
         f"Please choose one of the following {list(SITK_INTERPOLATOR_DICT.keys())}.")

    assert image.GetDimension() == len(new_spacing), \
        (f"Input is {image.GetDimension()}-dimensional while "
         f"the new spacing is {len(new_spacing)}-dimensional.")

    interpolator = SITK_INTERPOLATOR_DICT[interpolator]
    spacing = image.GetSpacing()
    size = image.GetSize()
    new_size = [
        int(round(siz * spac / n_spac))
        for siz, spac, n_spac in zip(size, spacing, new_spacing)
    ]
    return sitk.Resample(
        image,
        new_size,  # size
        sitk.Transform(),  # transform
        interpolator,  # interpolator
        image.GetOrigin(),  # outputOrigin
        new_spacing,  # outputSpacing
        image.GetDirection(),  # outputDirection
        default_value,  # defaultPixelValue
        image.GetPixelID())  # outputPixelType
