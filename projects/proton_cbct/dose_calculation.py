import sys

sys.path.append('.')

from pathlib import Path

from pyrad.interfaces import dose_calculation, utils

# Organs at risk for thoracic cancer
OARS = [{"label": "Esophagus", "penalty": 300}, 
{"label": "Lung_L", "penalty": 300},
{"label": "Lung_R", "penalty": 300,},
{"label": "Spinal_Cord", "penalty": 300}]

TARGETS = [{"label": "CTV1", "penalty": 1000}]
OTHERS = [{"label": "BODY", "penalty": 100}]

def main(args):
    dataset_path = args.dataset_path.resolve()
    pyrad_dose_calculation = dose_calculation.DoseCalculation(config="./projects/cbct_to_ct/configs/plan_config.yaml")

    for patient in dataset_path.iterdir():
        # Walk only through directories
        if patient.is_dir():
            CT = patient / "deformed.nrrd"
            CBCT = patient / "target.nrrd"
            sCT = patient / "translated.nrrd"
            body_mask = patient / "BODY.nrrd"

            if not (CT.exists() and CBCT.exists() and sCT.exists() and body_mask.exists()):
                print(f"Skipping patient {patient} as one of the mandatory files don't exist")
                continue


            target_masks = utils.fetch_masks_from_config(patient, TARGETS)
            oar_masks = utils.fetch_masks_from_config(patient, OARS)
            other_masks = utils.fetch_masks_from_config(patient, OTHERS)

            if not target_masks:
                print(f"Skipping patient {patient} ... No target mask for dose calculation")
                return {}

            masks = {
                "TARGET": target_masks,
                "OAR": oar_masks,
                "OTHER": other_masks
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Compute dose distributions for CBCT, CT and sCT scans" \
        "and provides gamma index analysis between CT-CBCT and CT-sCT"
        )

    parser.add_argument("dataset_path", help="Path to dataset", type=Path)
    args = parser.parse_args()

    main(args)
