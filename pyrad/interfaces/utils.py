
from pathlib import Path
from oct2py import octave as oc

def add_oc_paths():
    """
    Add octave paths from the pyrad - matrad organization
    """
    matRad_path = Path("./matRad").resolve()
    pyrad_path = Path("./pyrad").resolve()

    assert matRad_path.exists(), "matRad folder not found, please init the matRad submodule"

    # Add matrad and pyrad paths to .m files
    oc.addpath(str(matRad_path))
    oc.addpath(str(pyrad_path / "src"))

    # Add matrad tools such as gamma index computation
    oc.addpath(str(matRad_path / "tools"))
    oc.addpath(str(pyrad_path / "utils"))

def compute_gamma_index(dose1, dose2, resolution, dose_difference=3, dta=3, n=1):
    pass_rate = oc.matRad_gammaIndex(dose1, dose2, resolution, [dose_difference, dta], nout=1)

    return None, pass_rate