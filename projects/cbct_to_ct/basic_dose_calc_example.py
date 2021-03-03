import sys

sys.path.append('.')

from pyrad.matrad_dose_calc_wrapper import MatRadDoseCalcWrapper

def main():

    masks = {
        "TARGET": ['/home/suraj/Repositories/data/matRad_test/CTVcervixFull.nrrd'],
        "OAR": ['/home/suraj/Repositories/data/matRad_test/BLADDER.nrrd',
                '/home/suraj/Repositories/data/matRad_test/BOWELAREA.nrrd'],
        "OTHER": ['/home/suraj/Repositories/data/matRad_test/BODY.nrrd']
    }

    dose_calc = MatRadDoseCalcWrapper(".", "./projects/cbct_to_ct/plan_config.yaml")
    dose_calc("/home/suraj/Repositories/data/matRad_test/deformed.nrrd", masks)


if __name__ == "__main__":
    main()
