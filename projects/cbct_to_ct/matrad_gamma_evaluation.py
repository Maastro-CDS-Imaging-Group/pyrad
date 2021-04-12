from pathlib import Path
import SimpleITK as sitk
import sys
import pandas as pd
import numpy as np
from oct2py import Oct2Py

sys.path.append('.')
from pyrad.interfaces import utils

GAMMA_OPTS = {
    'dose_percent_threshold': 3,
    'distance_mm_threshold': 3,
}

def main(args):
    dataset_path = args.dataset_path.resolve()
    outdir = args.output_dir.resolve()
    df = pd.DataFrame()
    oc = Oct2Py()

    utils.add_oc_paths(oc)

    for folder in dataset_path.iterdir():
        folder = folder / "dose"
        if folder.is_dir():
            CT_path = folder / "ct_dose.nrrd"
            CBCT_path = folder / "cbct_dose.nrrd"
            sCT_path = folder / "sct_dose.nrrd"

            if not (CT_path.exists() and CBCT_path.exists() and sCT_path.exists()):
                print(f"Skipping patient {folder}")
                continue
                    
            patient_dir = outdir / folder.parent.stem
            print(f"Computing for patient {folder.parent.stem}")
            CT = sitk.ReadImage(str(CT_path))
            CBCT = sitk.ReadImage(str(CBCT_path))
            sCT = sitk.ReadImage(str(sCT_path))

            resolution = list(sCT.GetSpacing())
            CT = sitk.GetArrayFromImage(CT)
            CT = np.transpose(CT, (2, 1, 0))

            CBCT = sitk.GetArrayFromImage(CBCT)
            CBCT = np.transpose(CBCT, (2, 1, 0))

            sCT = sitk.GetArrayFromImage(sCT)
            sCT = np.transpose(sCT, (2, 1, 0))


            _, pass_rate = utils.compute_gamma_index(CT, CBCT, resolution, \
                 dose_difference=GAMMA_OPTS['dose_percent_threshold'], dta=GAMMA_OPTS['distance_mm_threshold'])
            print(f"Original pass rate: {pass_rate}")

            _, pass_rate = utils.compute_gamma_index(CT, sCT, resolution, \
                dose_difference=GAMMA_OPTS['dose_percent_threshold'], dta=GAMMA_OPTS['distance_mm_threshold'])
            print(f"Translated pass rate: {pass_rate}")


    if outdir.exists():
        df.to_csv(outdir / "metrics.csv")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Gamma distribution comparison between two CBCT-CT and sCT-CT")

    parser.add_argument("dataset_path", help="Path to dataset", type=Path)

    # Output dir to store dose maps and gamma index maps
    parser.add_argument("--output_dir",
                        help="Path where the output will be stored",
                        default="out",
                        type=Path)

    args = parser.parse_args()

    main(args)
