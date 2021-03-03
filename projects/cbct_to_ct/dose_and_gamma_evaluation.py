import sys

sys.path.append('.')

from pathlib import Path

from pyrad.matrad_dose_calc_wrapper import MatRadDoseCalcWrapper

OARS = ["BOWELAREA", "BLADDER"]
TARGETS = ["CTVcervix", "CTV"]

def main(args):
    dataset_path = args.dataset_path.resolve()
    output_dir = args.output_dir.resolve()
    dose_calc = MatRadDoseCalcWrapper("./projects/cbct_to_ct/plan_config.yaml")

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

            target_masks, oar_masks = [], []

            for target in TARGETS:
                target_masks.extend(list(patient.glob(f"*{target}*")))
            
            for oar in OARS:
                oar_masks.extend(list(patient.glob(f"*{oar}*")))

            if not target_masks:
                print(f"Skipping patient {patient} ... No target mask for dose calculation")
                continue

            masks = {
                "TARGET": target_masks,
                "OAR": oar_masks,
                "OTHER": [body_mask]
            }

            print("Peforming dose calculation for CT ...")
            dose_calc(CT, masks, save_path=patient/"ct_dose.nrrd")
            CT_dose = dose_calc.get_dose_map()

            print("Peforming dose calculation for CBCT ...")
            dose_calc(CBCT, masks, save_path=patient/"cbct_dose.nrrd")
            CBCT_dose = dose_calc.get_dose_map()

            print("Peforming dose calculation for sCT ...")
            dose_calc(sCT, masks, save_path=patient/"sct_dose.nrrd")
            sCT_dose = dose_calc.get_dose_map()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Compute dose distributions for CBCT, CT and sCT scans" \
        "and provides gamma index analysis between CT-CBCT and CT-sCT"
        )

    parser.add_argument("dataset_path", help="Path to dataset", type=Path)

    # Output dir to store dose maps and gamma index maps
    parser.add_argument("--output_dir", help="Path where the output will be stored", default="out", type=Path)

    args = parser.parse_args()

    main(args)
