import sys

sys.path.append('.')

from pyrad.interfaces import dose_calculation

def main():

    masks = {
        "TARGET": ['/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/CTVcervixFull.nrrd'],
        "OAR": ['/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/BLADDER.nrrd',
                '/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/BOWELAREA.nrrd'],
        "OTHER": ['/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/BODY.nrrd']
    }

    pyrad_dose_calculation = dose_calculation.DoseCalculation()
    pyrad_dose_calculation.run("/home/suraj/Repositories/data/NKI/evaluation_dataset/21006229/deformed.nrrd", masks)

if __name__ == "__main__":
    main()
