from typing import Optional, Tuple, List
from dataclasses import dataclass
from omegaconf import MISSING, II

@dataclass
class SteeringProperties:
    # Angles at which the beams are to be positioned
    gantryAngles: Optional[List] = None

    # Bixel width: https://medical-dictionary.thefreedictionary.com/bixel
    bixelWidth: int = 5

@dataclass
class TreatmentPlanConfig:
    # Steering properties determining how the beam is to be steered
    propStf: Optional[SteeringProperties] = None
    
    # Radiation mode: photons, protons, carbon
    radiationMode: str = "photons"
    
    # Number of fractions for the treatment
    numOfFractions: int = 30

    # machine parameters
    machine: str = "Generic"

