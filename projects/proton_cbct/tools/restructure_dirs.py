from pathlib import Path
import shutil

def main(args):
    registered_path = args.registered_path.resolve()
    translated_path = args.translated_path.resolve()
    
    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)

    shutil.copytree(registered_path, args.output_dir)

    for patient in args.output_dir.iterdir():
        if patient.is_dir() and (translated_path / patient).is_dir():
            translated = (translated_path / patient.stem / "target.nrrd").resolve()
            shutil.copy(translated, patient / "translated.nrrd")

  
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("registered_path", help="Path to dataset", type=Path)
    parser.add_argument("translated_path", help="Path to translated dataset", type=Path)
    
    parser.add_argument("--output_dir", help="Path where processing output will be stored", default="out", type=Path)

    args = parser.parse_args()

    main(args)
