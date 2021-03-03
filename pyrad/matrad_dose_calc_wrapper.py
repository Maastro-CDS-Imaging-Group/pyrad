import logging
from pathlib import Path

import numpy as np
import SimpleITK as sitk
import yaml
from oct2py import Oct2Py, get_log
from oct2py import octave as oc


class MatRadDoseCalcWrapper:
    def __init__(self, config):
        self.setup_logging()

        matRad_path = Path("./matRad").resolve()
        pyrad_path = Path("./pyrad").resolve()

        assert matRad_path.exists(), "matRad folder not found, please init the matRad submodule"

        oc.addpath(str(matRad_path))
        oc.addpath(str(pyrad_path))

        # Add matrad tools suchas gamma index computation
        oc.addpath(str(matRad_path / "tools"))
        oc.addpath(str(pyrad_path / "utils"))

        self.set_config(config)

    def setup_logging(self):
        oc_logger = Oct2Py(logger=get_log())
        oc_logger.logger = get_log('new_log')
        oc_logger.logger.setLevel(logging.INFO)

    def __call__(self, ct: Path, masks: dict, save_path: Path = None):
        self.ct = Path(ct)
        self.masks = self.process_masks(masks)

        self.compute_dose_map()
        
        if save_path is None:
            save_path = self.ct.resolve().parent / "dose_map.nrrd"
            
        self.save_dose_map(str(save_path))

    def set_config(self, config_path):
        self.config = None
        if config_path is not None:
            config_path = Path(config_path).resolve()
            with open(str(config_path), "r") as fp:
                self.config = yaml.full_load(fp)
        

    def process_masks(self, masks):
        assert "TARGET" in masks
        processed_masks = {}

        # Add targets to all masks
        processed_masks["masks"] = [v for v in masks["TARGET"]]
        # If oars are provided, add it to masks
        if "OAR" in masks:
            processed_masks["masks"].extend(masks["OAR"])
        # If masks that are neither OAR or TARGETS are provided
        if "OTHER" in masks:
            processed_masks["masks"].extend(masks["OTHER"])

        for key in masks:
            masks[key] = [Path(v).resolve() for v in masks[key]]
            processed_masks[key] = {path.stem:str(path) for path in masks[key]}

        processed_masks["masks"] = [str(v) for v in processed_masks["masks"]]

        return processed_masks
        
    def compute_dose_map(self):
        self.dose, self.metadata = oc.dose_calc_fn(self.config, str(self.ct), self.masks, nout=2)

    def compute_gamma_index(self, dose1, dose2, resolution, dose_difference=3, dta=3, n=1):
        pass_rate = oc.matRad_gammaIndex(dose1, dose2, resolution, [dose_difference, dta], nout=1)

        return None, pass_rate

    def get_dose_map(self):
        self.dose = self.dose.transpose(2, 0, 1)
        dose_image = sitk.GetImageFromArray(self.dose)

        ct_image = sitk.ReadImage(str(self.ct))
        dose_image.CopyInformation(ct_image)
        return dose_image

    def save_dose_map(self, save_path):
        dose_image = self.get_dose_map()
        sitk.WriteImage(dose_image, save_path, True)
