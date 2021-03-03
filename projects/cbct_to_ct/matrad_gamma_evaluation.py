from pathlib import Path
import SimpleITK as sitk
import sys
import pandas as pd
import numpy as np

sys.path.append('.')
from pyrad.utils import dose_eval, image_utils
from pyrad.matrad_dose_calc_wrapper import MatRadDoseCalcWrapper


def main(args):
    dataset_path = args.dataset_path.resolve()
    outdir = args.output_dir.resolve()
    df = pd.DataFrame()

    dose_calc = MatRadDoseCalcWrapper(".", "./projects/cbct_to_ct/plan_config.yaml")

    for folder in dataset_path.iterdir():
        if folder.is_dir():
            CT_path = folder / "ct_dose.nrrd"
            CBCT_path = folder / "cbct_dose.nrrd"
            sCT_path = folder / "sct_dose.nrrd"

            if not (CT_path.exists() and CBCT_path.exists() and sCT_path.exists()):
                print(f"Skipping patient {folder}")
                continue
                    
            patient_dir = outdir / folder.stem
            print(f"Computing for patient {folder.stem}")
            CT = sitk.ReadImage(str(CT_path))
            CBCT = sitk.ReadImage(str(CBCT_path))
            sCT = sitk.ReadImage(str(sCT_path))

            resolution = list(CT.GetSpacing())
            CT = sitk.GetArrayFromImage(CT)
            CBCT = sitk.GetArrayFromImage(CBCT)
            sCT = sitk.GetArrayFromImage(sCT)

            _, pass_rate = dose_calc.compute_gamma_index(CT, CBCT, resolution, dose_difference=2, dta=2)
            print(f"Original pass rate: {pass_rate}")

            _, pass_rate = dose_calc.compute_gamma_index(CT, sCT, resolution, dose_difference=2, dta=2)
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
