import sys

sys.path.append('.')

from pyrad.interfaces import dose_calculation


def main():
    treatment_plan_config = "./projects/cbct_to_ct/configs/plan_config.yaml"
    
    CT = "/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/deformed.nrrd"
    masks = {
        "TARGET": [
            '/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/CTVcervixFull.nrrd'
        ],
        "OAR": [
            '/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/BLADDER.nrrd',
            '/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/BOWELAREA.nrrd'
        ],
        "OTHER": [
            '/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/BODY.nrrd'
        ]
    }

    pyrad_dose_calculation = dose_calculation.DoseCalculation(
        config=treatment_plan_config)
    pyrad_dose_calculation.run(CT, masks)


if __name__ == "__main__":
    main()
