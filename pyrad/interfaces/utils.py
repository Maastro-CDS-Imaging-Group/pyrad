
from pathlib import Path
from oct2py import Oct2Py
import numpy as np

def add_oc_paths(octave_interface):
    """
    Add octave paths from the pyrad - matrad organization
    """
    matRad_path = Path("./matRad").resolve()
    pyrad_path = Path("./pyrad").resolve()

    assert matRad_path.exists(), "matRad folder not found, please init the matRad submodule"

    # Add matrad and pyrad paths to .m files
    octave_interface.addpath(str(matRad_path))
    octave_interface.addpath(str(pyrad_path / "src"))

    # Add matrad tools such as gamma index computation
    octave_interface.addpath(str(matRad_path / "tools"))
    octave_interface.addpath(str(pyrad_path / "utils"))

def fetch_masks_from_config(patient, mask_set):
    masks = []
    for mask in mask_set:
        if isinstance(mask["label"], list):
            for mask_stem in mask["label"]:
                mask["path"] = (patient / mask_stem).with_suffix(".nrrd")

                # Check if the label provided in the list of labels is 
                # a valid path
                if mask["path"].exists():
                    break

        else:
            mask["path"] = (patient / mask["label"]).with_suffix(".nrrd")
            
        # If path is not valid, the mask is not considered
        if not mask["path"].exists():
            continue

        masks.append(mask)

    return masks

def compute_gamma_index(dose1, dose2, resolution, dose_difference=3, dta=3, n=0, local=False):
    # Create new octave instance for gamma index inorder to isolate it.
    oc = Oct2Py()
    add_oc_paths(oc)
    if local:
        globallocal = 'local'
    else:
        globallocal = 'global'

    pass_rate = oc.matRad_gammaIndex(dose1, dose2, resolution, [dose_difference, dta], globallocal, n, nout=1)
    return None, pass_rate