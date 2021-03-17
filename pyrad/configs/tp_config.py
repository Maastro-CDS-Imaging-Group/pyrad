from typing import Optional, Tuple, List
from dataclasses import dataclass
from omegaconf import MISSING, II

@dataclass
class SteeringProperties:
    # Angles at which the beams are to be positioned
    gantryAngles: Optional[List] = None


@dataclass
class TreatmentPlanConfig:
    # Steering properties determining how the beam is to be steered
    propStf: Optional[SteeringProperties] = None

