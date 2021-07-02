from pathlib import Path
import SimpleITK as sitk
import sys
import pandas as pd
import numpy as np
from oct2py import Oct2Py
import logging

sys.path.append('.')
from pyrad.interfaces import utils
# List of dicts specifying gamma options
GAMMA_OPTS = [
    {
    'dose_percent_threshold': 1,
    'distance_mm_threshold': 1,
},
{
    'dose_percent_threshold': 2,
    'distance_mm_threshold': 2,
}, {
    'dose_percent_threshold': 1,
    'distance_mm_threshold': 2,
}, {
    'dose_percent_threshold': 3,
    'distance_mm_threshold': 3,
}]

logger = logging.getLogger(__name__)

def main(args):
    dataset_path = args.dataset_path.resolve()
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
                logger.warning(f"Skipping patient {folder}")
                continue
                    
            logger.info(f"Computing for patient {folder.parent.stem}")
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

            metric = {}
            metric["Patient"] = folder.parent.stem


            for gamma_opt in GAMMA_OPTS:
                logger.info(f"Computing for {gamma_opt}")
                _, pass_rate = utils.compute_gamma_index(CT, CBCT, resolution, \
                    dose_difference=gamma_opt['dose_percent_threshold'], dta=gamma_opt['distance_mm_threshold'])
                metric[f"CBCT_passing_rate_{gamma_opt['dose_percent_threshold']}%_{gamma_opt['distance_mm_threshold']}mm"] = pass_rate
                logger.info(f"CBCT pass rate={pass_rate}")


                _, pass_rate = utils.compute_gamma_index(CT, sCT, resolution, \
                    dose_difference=gamma_opt['dose_percent_threshold'], dta=gamma_opt['distance_mm_threshold'])
                metric[f"SCT_passing_rate_{gamma_opt['dose_percent_threshold']}%_{gamma_opt['distance_mm_threshold']}mm"] = pass_rate
                logger.info(f"sCT pass rate={pass_rate}")

            df = df.append(metric, ignore_index=True)

    df.to_csv(dataset_path / "matrad_gamma_results.csv")



def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel,
                        stream=sys.stdout,
                        format=logformat,
                        datefmt="%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Gamma distribution comparison between two CBCT-CT and sCT-CT")

    parser.add_argument("dataset_path", help="Path to dataset", type=Path)

    parser.add_argument("-v",
                        "--verbose",
                        dest="loglevel",
                        help="set loglevel to INFO",
                        action="store_const",
                        const=logging.INFO)



    args = parser.parse_args()
    setup_logging(args.loglevel)
    main(args)
