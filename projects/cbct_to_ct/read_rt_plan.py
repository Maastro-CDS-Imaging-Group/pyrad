import pydicom
from pathlib import Path

def list_beams(plan_dataset):
    """Summarizes the RTPLAN beam information in the dataset."""
    lines = ["{name:^13s} {num:^8s} {gantry:^8s} {ssd:^11s}".format(
        name="Beam name", num="Number", gantry="Gantry", ssd="SSD (cm)")]
    for beam in plan_dataset.BeamSequence:
        cp0 = beam.ControlPointSequence[0]
        SSD = float(cp0.SourceToSurfaceDistance / 10)
        lines.append("{b.BeamName:^13s} {b.BeamNumber:8d} "
                     "{gantry:8.1f} {ssd:8.1f}".format(b=beam,
                                                       gantry=cp0.GantryAngle,
                                                       ssd=SSD))
    return "\n".join(lines)

def main(args):
    dataset_path = args.dataset_path.resolve()

    for fn in dataset_path.rglob("*.dcm"):
        dataset  = pydicom.dcmread(fn)
        print(dataset)
        print(list_beams(dataset))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("dataset_path", help="Path to dataset where RT plan .dcm can be found", type=Path)

    args = parser.parse_args()

    main(args)