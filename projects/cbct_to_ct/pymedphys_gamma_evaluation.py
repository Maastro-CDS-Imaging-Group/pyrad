import sys
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk

sys.path.append('.')
import logging

from pyrad.utils import dose_eval, image_utils

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)

# Options for gamma calculation.
# https://docs.pymedphys.com/lib/howto/gamma/effect-of-noise.html
GAMMA_OPTS = {
    'dose_percent_threshold': 2,
    'distance_mm_threshold': 1,
    'local_gamma': False
}

# Try out 1%/1mm and 1%/2mm
# Variations in clinical factors need not be considered


def dose_evaluation(CT, CBCT, sCT, patient_dir='patient'):
    patient_dir = Path(patient_dir).resolve()
    patient_dir.mkdir(exist_ok=True, parents=True)

    metric_dict = {
        'patient': patient_dir.stem
    }

    # Compute dose differences for CT-CBCT and sCT-CT
    CBCT_dose_diff = dose_eval.calculate_dose_diff(CT, CBCT)
    sCT_dose_diff = dose_eval.calculate_dose_diff(CT, sCT)


    metric_dict.update({f'cbct_dose_diff_{k}': v for k, v in image_utils.get_abs_value_stats(CBCT_dose_diff).items()})
    metric_dict.update({f'sct_dose_diff_{k}': v for k, v in image_utils.get_abs_value_stats(sCT_dose_diff).items()})

    sitk.WriteImage(CBCT_dose_diff, str(patient_dir / "cbct_dose_diff.nrrd"))
    sitk.WriteImage(sCT_dose_diff, str(patient_dir / "sct_dose_diff.nrrd"))
    
    # Save image preview

    image_utils.save_dose_diff(CBCT_dose_diff, label='Original - Relative dose difference', dir=patient_dir, limit=(-1, 1))
    image_utils.save_dose_diff(sCT_dose_diff, label='Translated - Relative dose difference', dir=patient_dir, limit=(-1, 1))

    # Compute gamma passing rates for CT-CBCT and sCT-CT
    CBCT_gamma, passing_rate_CBCT = dose_eval.calculate_gamma(CT, CBCT, GAMMA_OPTS)
    metric_dict['cbct_passing_rate'] = passing_rate_CBCT
    print(f"CBCT passing rate: {passing_rate_CBCT}")
    sitk.WriteImage(CBCT_gamma, str(patient_dir / "cbct_gamma.nrrd"))
    image_utils.save_gamma(CBCT_gamma, label='original_gamma', dir=patient_dir)

    sCT_gamma, passing_rate_sCT = dose_eval.calculate_gamma(CT, sCT, GAMMA_OPTS)
    metric_dict['sct_passing_rate'] = passing_rate_sCT
    print(f"sCT passing rate: {passing_rate_sCT}")
    sitk.WriteImage(sCT_gamma, str(patient_dir / "sct_gamma.nrrd"))
    
    # Save image preview
    image_utils.save_gamma(sCT_gamma, label='translated_gamma', dir=patient_dir)

    return metric_dict


def main(args):
    dataset_path = args.dataset_path.resolve()
    outdir = args.output_dir.resolve()
    df = pd.DataFrame()

    for folder in dataset_path.iterdir():
        if folder.is_dir():
            CT_path = folder / "ct_dose.nrrd"
            CBCT_path = folder / "cbct_dose.nrrd"
            sCT_path = folder / "sct_dose.nrrd"

            if not (CT_path.exists() and CBCT_path.exists() and sCT_path.exists()):
                logger.warning(f"Skipping patient {folder}")
                continue
                    

            logger.info(f"Computing for patient {folder.stem}")

            patient_dir = outdir / folder.stem
            CT_image = sitk.ReadImage(str(CT_path))
            CBCT_image = sitk.ReadImage(str(CBCT_path))
            sCT_image = sitk.ReadImage(str(sCT_path))

            metric_dict = dose_evaluation(CT_image, CBCT_image, sCT_image, patient_dir=patient_dir)

            df = df.append(metric_dict, ignore_index=True)

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
