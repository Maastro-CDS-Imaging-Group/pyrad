import logging
from pathlib import Path

import numpy as np
import SimpleITK as sitk
import yaml
from oct2py import Oct2Py, get_log
from omegaconf import OmegaConf
from loguru import logger

from pyrad.interfaces import utils
from pyrad.configs import tp_config


class DoseCalculation:
    def __init__(self, config=None, projects_dir=None):
        self.setup_environment(projects_dir)
        self.set_treatment_plan(config)

    def setup_environment(self, projects_dir=None):
        logger.add('dose_calculation.log', level='INFO')
        self.oc = Oct2Py(logger=logger)
        utils.add_oc_paths(self.oc)
        if projects_dir is not None:
            self.oc.addpath(projects_dir)

    def run(self, ct: Path, masks: dict, save_path: Path = None):
        self.ct = Path(ct)
        self.masks = self.process_masks(masks)

        self.oc.logger.info(f"Patient: {ct.parent.stem}, Masks: {self.masks}")
        # Matrad dose_calc_fn is called
        self.dose, self.metadata = self.oc.run_dose_calculation(self.config, str(self.ct), self.masks, nout=2)
        self.dose = self.dose.transpose(2, 0, 1)

        if save_path is None:
            save_path = self.ct.resolve().parent / "dose_map.nrrd"
            
        self.save_dose_map(str(save_path))

    def set_treatment_plan(self, config_path):
        conf = OmegaConf.structured(tp_config.TreatmentPlanConfig)
        yaml_file = OmegaConf.load(config_path)

        self.config = OmegaConf.merge(conf, yaml_file)

        # Convert DictConfig to Dict 
        self.config = OmegaConf.to_container(self.config)

    def process_masks(self, masks):
        assert "TARGET" in masks, "Dose calculation needs a TARGET mask"
        processed_masks = {}

        # Add targets to all masks
        processed_masks["masks"] = [v["path"] for v in masks["TARGET"]]
        # If oars are provided, add it to masks
        if "OAR" in masks:
            processed_masks["masks"].extend([v["path"] for v in masks["OAR"]])
        # If masks that are neither OAR or TARGETS are provided
        if "OTHER" in masks:
            processed_masks["masks"].extend([v["path"] for v in masks["OTHER"]])

        for key in masks:
            # The format for a processed mask is {"CTVcervix": (path, penalty)}
            processed_masks[key] = {Path(v["path"]).resolve().stem:(str(v["path"]), v["penalty"]) for v in masks[key]}

        processed_masks["masks"] = [str(v) for v in processed_masks["masks"]]

        return processed_masks


    def get_dose_map(self):
        """
        Get dose map SITK Image from dose computed with matrad
        """
        dose_image = sitk.GetImageFromArray(self.dose)
        ct_image = sitk.ReadImage(str(self.ct))
        dose_image.CopyInformation(ct_image)
        return dose_image

    def save_dose_map(self, save_path):
        """
        Save dose map SITK Image to nrrd
        """
        dose_image = self.get_dose_map()
        sitk.WriteImage(dose_image, save_path, True)
