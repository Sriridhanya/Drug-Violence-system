import os
import re
from pathlib import Path

# CHANGE THIS to where your extracted dataset folder is
RAW = Path("weapon_detection")  # if you run this inside the extracted folder
# Example if you run from drug-violence-system:
# RAW = Path("datasets/weapon_detection_raw/weapon_detection")

# Output folder (clean dataset for training)
OUT = Path("weapon_detection_yolo")
TRAIN_L = OUT / "train" / "labels"
VAL_L   = OUT / "val" / "labels"

# 9 classes
CLASS_NAMES = [
    "Automatic Rifle",
    "Bazooka",
    "Grenade Launcher",
    "Handgun",
    "Knife",
    "Shotgun",
    "SMG",
    "Sniper",
    "Sword",
]
NAME_TO_ID = {n.lower(): i for i, n in enumerate(CLASS_NAMES)}

def weapon_type_from_filename(filename: str) -> str:
    # "Automatic Rifle_10.jpeg" -> "automatic rifle"
    base = Path(filename).stem
    # split at last underscore number
    # keeps "Grenade Launcher" etc.
    parts = base.rsplit("_", 1)
    weapon = parts[0].strip().lower()
    return weapon

def rewrite_labels(src_label_dir: Path, dst_label_dir: Path):
    dst_label_dir.mkdir(parents=True, exist_ok=True)
    for label_path in src_label_dir.glob("*.txt"):
        weapon = weapon_type_from_filename(label_path.name)
        if weapon not in NAME_TO_ID:
            # Skip unknown label files (if any)
            print(f"Skipping unknown weapon type: {weapon} from {label_path.name}")
            continue

        cls_id = NAME_TO_ID[weapon]
        lines_out = []

        content = label_path.read_text(encoding="utf-8").strip().splitlines()
        for line in content:
            if not line.strip():
                continue
            parts = line.split()
            # YOLO format: class x y w h
            # Replace class with our mapped class id
            parts[0] = str(cls_id)
            lines_out.append(" ".join(parts))

        (dst_label_dir / label_path.name).write_text("\n".join(lines_out) + "\n", encoding="utf-8")

def copy_tree(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        outp = dst / rel
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_bytes(p.read_bytes())

def main():
    # Copy images+labels to clean folder
    copy_tree(RAW / "train" / "images", OUT / "train" / "images")
    copy_tree(RAW / "val"   / "images", OUT / "val"   / "images")

    # Rewrite labels into 9-class labels
    rewrite_labels(RAW / "train" / "labels", TRAIN_L)
    rewrite_labels(RAW / "val"   / "labels", VAL_L)

    # Write data.yaml
    yaml = f"""path: {OUT.resolve()}
train: train/images
val: val/images

nc: {len(CLASS_NAMES)}
names: {CLASS_NAMES}
"""
    (OUT / "data.yaml").write_text(yaml, encoding="utf-8")
    print("✅ Dataset prepared at:", OUT.resolve())
    print("✅ data.yaml created at:", (OUT / "data.yaml").resolve())

if __name__ == "__main__":
    main()