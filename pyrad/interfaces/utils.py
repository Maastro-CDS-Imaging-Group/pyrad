
from pathlib import Path
from oct2py import Oct2Py

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

def compute_gamma_index(dose1, dose2, resolution, dose_difference=3, dta=3, n=1):
    # Create new octave instance for gamma index inorder to isolate it.
    oc = Oct2Py()
    add_oc_paths(oc)

    pass_rate = oc.matRad_gammaIndex(dose1, dose2, resolution, [dose_difference, dta], nout=1)
    return None, pass_rate