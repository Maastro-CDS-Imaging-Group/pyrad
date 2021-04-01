import sys

sys.path.append('.')

from pathlib import Path

import pandas as pd
import SimpleITK as sitk
from pyrad.interfaces import dose_calculation, utils
from pyrad.utils import dose_eval, image_utils

# Organs at risk for cervical cancer
OARS = ["BOWELAREA", "BLADDER", "RECTUM", "RING", "SMALLBOWEL", "SIGMOID", "Ring"]
TARGETS = ["CTV"]

# List of dicts specifying gamma options
GAMMA_OPTS = [{
    'dose_percent_threshold': 2,
    'distance_mm_threshold': 2,
}, {
    'dose_percent_threshold': 1,
    'distance_mm_threshold': 2,
}, {
    'dose_percent_threshold': 1,
    'distance_mm_threshold': 1,
}]


def main(args):
    dataset_path = args.dataset_path.resolve()
    df = pd.DataFrame()
    patient_dirs = [patient for patient in dataset_path.iterdir() if patient.is_dir()]

    if args.cores > 1:
        print(f"Running in multiprocessing mode with cores: {args.cores}")
        with multiprocessing.Pool(processes=args.cores) as pool:
            metrics_dict = pool.starmap(calculate_dose, patient_dirs)
            for metric_dict in metrics_dict:
                df= df.append(metric_dict, ignore_index=True)
    else:
        print(f"Running in main process only")
        for patient in patient_dirs:
            metric_dict = calculate_dose(patient)
            df = df.append(metric_dict, ignore_index=True)
            break

    df.to_csv("dosimetrics.csv")


def calculate_dose(patient):
    pyrad_dose_calculation = dose_calculation.DoseCalculation(config="./projects/cbct_to_ct/configs/plan_config.yaml")
    CT = patient / "deformed.nrrd"
    CBCT = patient / "target.nrrd"
    sCT = patient / "translated.nrrd"
    body_mask = patient / "BODY.nrrd"

    if not (CT.exists() and CBCT.exists() and sCT.exists() and body_mask.exists()):
        print(f"Skipping patient {patient} as one of the mandatory files don't exist")
        return {}

    metric_dict = {
    'patient': patient.stem
    }

    target_masks, oar_masks = [], []

    for target in TARGETS:
        target_masks.extend(list(patient.glob(f"*{target}*")))
    
    for oar in OARS:
        oar_masks.extend(list(patient.glob(f"*{oar}*")))

    if not target_masks:
        print(f"Skipping patient {patient} ... No target mask for dose calculation")
        return {}

    masks = {
        "TARGET": target_masks,
        "OAR": oar_masks,
        "OTHER": [body_mask]
    }

    print("Peforming dose calculation for CT ... \n")
    print(f"Targets: {target_masks} and Organs at Risk: {oar_masks}")

    pyrad_dose_calculation.run(CT, masks, save_path=patient/"ct_dose.nrrd")
    CT_dose = pyrad_dose_calculation.get_dose_map()

    print("Peforming dose calculation for CBCT ...")
    pyrad_dose_calculation.run(CBCT, masks, save_path=patient/"cbct_dose.nrrd")
    CBCT_dose = pyrad_dose_calculation.get_dose_map()

    print("Peforming dose calculation for sCT ...")
    pyrad_dose_calculation.run(sCT, masks, save_path=patient/"sct_dose.nrrd")
    sCT_dose = pyrad_dose_calculation.get_dose_map()

    # Dosimetric Analysis
    metric_dict.update(dosimetric_analysis(CT_dose, CBCT_dose, prefix='CBCT', patient=patient))
    metric_dict.update(dosimetric_analysis(CT_dose, sCT_dose, prefix='sCT', patient=patient))

    return metric_dict


def dosimetric_analysis(target_dose, pred_dose, prefix='', patient='.'):
    metric_dict = {}

    dose_diff = dose_eval.calculate_dose_diff(target_dose, pred_dose)
    metric_dict.update({f'{prefix}_dose_diff_{k}': v for k, v in image_utils.get_stats(dose_diff).items()})
    sitk.WriteImage(dose_diff, str(patient / f"{prefix}_dose_diff.nrrd"))
            
    # Save image preview
    image_utils.save_dose_diff(dose_diff, label=f'{prefix} - Relative dose difference', dir=patient, limit=(-1, 1))

    # Gamma index analysis
    resolution = list(target_dose.GetSpacing())
    target_dose = sitk.GetArrayFromImage(target_dose)
    pred_dose = sitk.GetArrayFromImage(pred_dose)

    for gamma_opt in GAMMA_OPTS:
        _, pass_rate = utils.compute_gamma_index(target_dose, pred_dose, resolution, \
            dose_difference=gamma_opt['dose_percent_threshold'], dta=gamma_opt['distance_mm_threshold'])
        
        metric_dict[f"{prefix}_passing_rate_{gamma_opt['dose_percent_threshold']}%_{gamma_opt['distance_mm_threshold']}mm"] = pass_rate

    return metric_dict


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Compute dose distributions for CBCT, CT and sCT scans" \
        "and provides gamma index analysis between CT-CBCT and CT-sCT"
        )

    parser.add_argument("dataset_path", help="Path to dataset", type=Path)
    parser.add_argument("--cores", help="Number of cores for multiprocessing", default=1, type=int)

    args = parser.parse_args()

    main(args)
