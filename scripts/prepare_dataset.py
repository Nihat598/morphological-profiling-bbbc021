"""Copy the DAPI images used in this project from a local BBBC021 download
into the repository's data/ folder, next to the committed segmentation masks.

This is a script version of notebooks/01_data_extraction.ipynb.

Usage
-----
1. Download and unzip the six plates below from
   https://bbbc.broadinstitute.org/BBBC021 so that you have, e.g.
       <BBBC021_ROOT>/Week1_22123/*.tif
       <BBBC021_ROOT>/Week4_27801/*.tif
   (Nested layouts such as <ROOT>/BBBC021_v1_images_Week1_22123/Week1_22123/
   are also found automatically.)
2. Run:
       python scripts/prepare_dataset.py --bbbc021-root <BBBC021_ROOT>
"""

import argparse
import shutil
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
METADATA = REPO / "data" / "metadata" / "BBBC021_v1_image.csv"
DATA_DIR = REPO / "data"

WEEK1_PLATES = ["Week1_22123", "Week1_22141", "Week1_22161"]
WEEK4_PLATES = ["Week4_27801", "Week4_27821", "Week4_27861"]

# (compound in metadata, concentration in µM, plates, output sub-folder)
CONDITIONS = [
    ("DMSO", 0.0, WEEK1_PLATES + WEEK4_PLATES, "DMSO"),
    ("aphidicolin", 0.003, WEEK1_PLATES, "aphidicolin/concentration_0003"),
    ("aphidicolin", 10.0, WEEK1_PLATES, "aphidicolin/concentration_10"),
    ("mitomycin C", 0.003, WEEK4_PLATES, "mitomycin/concentration_0003"),
    ("mitomycin C", 10.0, WEEK4_PLATES, "mitomycin/concentration_10"),
]


def find_plate_dir(root: Path, plate: str) -> Path:
    candidates = [p for p in root.rglob(plate) if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"Plate folder '{plate}' not found under {root}")
    return candidates[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bbbc021-root", required=True, type=Path, help="Folder containing the unzipped BBBC021 plates")
    args = parser.parse_args()

    meta = pd.read_csv(METADATA, sep=";")
    total = 0
    for compound, conc, plates, out_sub in CONDITIONS:
        for plate in plates:
            rows = meta[
                (meta["Image_Metadata_Plate_DAPI"] == plate)
                & (meta["Image_Metadata_Compound"] == compound)
                & (meta["Image_Metadata_Concentration"].round(6) == round(conc, 6))
            ]
            src_dir = find_plate_dir(args.bbbc021_root, plate)
            dst_dir = DATA_DIR / out_sub / plate
            dst_dir.mkdir(parents=True, exist_ok=True)
            for fname in rows["Image_FileName_DAPI"]:
                shutil.copy2(src_dir / fname, dst_dir / fname)
            total += len(rows)
            print(f"{compound:12s} {conc:>6} µM  {plate}: {len(rows)} images -> {dst_dir.relative_to(REPO)}")
    print(f"Done: {total} DAPI images copied.")


if __name__ == "__main__":
    main()
