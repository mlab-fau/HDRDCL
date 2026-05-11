# HDRDCL — High Dynamic Range Detection in Challenging Lighting

Hey! Welcome to the label repository for **HDRDCL**, a dataset for object detection and segmentation in HDR images under challenging lighting conditions. This repo contains the annotation files (`.json`) for both subsets of the dataset. The source HDR images are *not* included here — you'll need to download them separately from the original datasets (links below).

> 📄 If you use this dataset, please cite our paper, citation found at the end of this repository.
>
> 🙏 **Please also cite the original source-image datasets** you use — our work would not be possible without them. Links and citations are listed under [Source datasets](#source-datasets--youll-need-these) below.

---

## What's in the dataset?

HDRDCL has two subsets, drawn from the same pool of 2,050 HDR images:

- **HDRDCL-det** — 2,050 images with bounding-box annotations (**20,042** instances across **62** classes)
- **HDRDCL-seg** — 630 images with instance segmentation masks (**5,052** polygon instances across **46** classes); every segmentation image is also in the detection set. Each seg `.json` also stores the redundant bounding box for each polygon, so a raw shape count is ~9,800; the mask count is the polygon count.

> 🎁 **Bonus image included.** One image (`Set7_Set7.hdr`) is our own custom capture and is bundled directly in this repo under [`sources/bonus/`](sources/bonus/) — `build_dataset.py` will pick it up automatically, no external download needed. It contributes 4 detection bboxes and 4 segmentation masks (already counted in the totals above). All other source images must be obtained from the original datasets linked below.

Images were selected using an automated filtering pipeline that keeps only scenes where HDR content provides genuine detection benefits over a standard single-exposure tone mapping approach. In other words, every image in here is one where LDR may struggle.

### Breakdown by source dataset

| Source dataset | Detection images | Detection instances | Segmentation images | Segmentation masks |
|---|---:|---:|---:|---:|
| HDR4RTT | 1,596 | 16,290 | 508 | 4,475 |
| IndoorHDRDataset2018 | 338 | 2,680 | 94 | 454 |
| Reinhard et al. (`images/`) | 62 | 512 | 19 | 68 |
| SYNS | 40 | 468 | 3 | 8 |
| UPIQ (`upiq_dataset/`) | 13 | 88 | 5 | 43 |
| 🎁 Bonus (`bonus/`, bundled) | 1 | 4 | 1 | 4 |
| **Total** | **2,050** | **20,042** | **630** | **5,052** |

Top classes overall: `person`, `bottle`, `chair`, `car`, `potted plant`, `cup`, `dining table`, `vase`.

---

## Label sets

Labels are organized by **source dataset** and then by **task** under `labels/`. Each `.json` is in [LabelMe](https://github.com/wkentaro/labelme) format — `rectangle` shapes are bounding boxes (detection); `polygon` shapes are instance masks (segmentation, generated via SAM2).

```
labels/
├── IndoorHDRDataset2018/
│   ├── detection/        338 json
│   └── segmentation/      94 json
├── SYNS/
│   ├── detection/         40 json
│   └── segmentation/       3 json
├── HDR4RTT/
│   ├── detection/       1596 json
│   └── segmentation/     508 json
├── upiq_dataset/
│   ├── detection/         13 json
│   └── segmentation/       5 json
├── images/                   ← Reinhard et al. reference set
│   ├── detection/         62 json
│   └── segmentation/      19 json
└── bonus/                    ← 🎁 our custom image, source bundled in sources/bonus/
    ├── detection/          1 json
    └── segmentation/       1 json
```

**Totals:** 2,050 detection labels · 630 segmentation labels.

---

## Source datasets — you'll need these!

The HDR source images come from several publicly available datasets. Download them from the links below and point `build_dataset.py` at your local copy.

### 🎯 HDR4RTT
An HDR dataset originally designed for object detection, which we re-labeled and extended with instance segmentation masks.

**Images in HDRDCL:** 1,596 detection · 508 segmentation

🔗 [Download HDR4RTT](<https://drive.inesctec.pt/s/dPwxsHWpxj8xynk>)

> Mukherjee et al., *"Backward Compatible Object Detection Using HDR Image Content"*, IEEE Access, 2020.

---

### 🌿 SYNS (Southampton-York Natural Scenes)
Natural outdoor scenes with a wide range of surface and lighting conditions.

**Images in HDRDCL:** 40 detection · 3 segmentation

🔗 [Download SYNS](<https://syns.soton.ac.uk/>) (Panorama)

> Adams et al., *"The Southampton-York Natural Scenes (SYNS) Dataset: Statistics of Surface Attitude"*, Scientific Reports, 2016.

---

### 📊 UPIQ (Unified Photometric Image Quality Dataset)
A photometric image quality dataset with HDR content.

**Images in HDRDCL:** 13 detection · 5 segmentation

🔗 [Download UPIQ](<https://www.repository.cam.ac.uk/bitstreams/016c5d46-dd55-458c-a6a9-29aa0ecedebe/download>)

> Mikhailiuk et al., *"UPIQ: Unified Photometric Image Quality Dataset"*, Apollo — University of Cambridge Repository, 2020.

---

### 🏠 IndoorHDRDataset2018
Indoor HDR panoramas used for illumination estimation research. *Reaching out to authors for dataset required*

**Images in HDRDCL:** 338 detection · 94 segmentation

🔗 [Download IndoorHDRDataset2018](<http://hdrdb.com/indoor/>)

> Gardner et al., *"Learning to Predict Indoor Illumination from a Single Image"*, SIGGRAPH Asia 2017.

---

### 📖 Reinhard et al. Reference Collection
A small set of HDR reference images from the classic HDR imaging textbook. These are tied to the book and don't have a standalone public download link — you'll need access to:

> Reinhard, Ward, Pattanaik, Debevec. *"High Dynamic Range Imaging: Acquisition, Display, and Image-Based Lighting"*, 2006.

**Images in HDRDCL:** 62 detection · 19 segmentation

---

### 🎁 Bonus (our own capture)
One custom HDR image (`Set7_Set7.hdr`) captured by us. The source image is **bundled in this repo** at [`sources/bonus/`](sources/bonus/) — `build_dataset.py` finds it automatically, no download needed.

**Images in HDRDCL:** 1 detection · 1 segmentation

## Getting started

### 1. Download the source datasets

Grab the datasets you need from the links above and place them somewhere on disk. The expected layout under your images root is:

```
IMAGES_DIR/
    IndoorHDRDataset2018/
    SYNS/
    upiq_dataset/
    HDR4RTT/
    images/          ← Reinhard et al. reference images
```

(`bonus/` is **not** required here — it's bundled in this repo at `sources/bonus/` and `build_dataset.py` reads it from there automatically.)

### 2. Clone this repo (labels)

```bash
git clone https://github.com/mlab-fau/HDRDCL
cd HDRDCL
```

### 3. Assemble the dataset with `build_dataset.py`

The script matches label `.json` files to their source `.exr`/`.hdr` images and assembles them into a clean output directory grouped by source dataset.

```bash
python build_dataset.py \
    --labels /path/to/this/repo \
    --images /path/to/source/images \
    --out /path/to/output \
    --mode symlink   # or copy / hardlink
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--labels` | hardcoded path | Directory containing label `.json` subfolders |
| `--images` | hardcoded path | Root directory of downloaded source datasets |
| `--out` | hardcoded path | Where to write the assembled dataset |
| `--mode` | `symlink` | How to place source images: `symlink`, `copy`, or `hardlink` |
| `--dry-run` | off | Preview pairings without writing anything |
| `--limit N` | 0 (all) | With `--dry-run`, show only first N pairings per label set |

**Tip:** Run with `--dry-run` first to make sure everything is finding its match before committing to a full copy.

### Output layout

```
OUTPUT_DIR/
    IndoorHDRDataset2018/
        detection/
            image_stem.json
            image_stem.exr     ← matched source image
        segmentation/
            ...
    SYNS/
        detection/
        segmentation/
    HDR4RTT/
        ...
    upiq_dataset/
        ...
    images/                    ← Reinhard et al.
        ...
```

## Citation

```bibtex
@inproceedings{merlos2026hdrdcl,
  title     = {HDRDCL: An HDR Object Detection and Segmentation Dataset for Evaluation in Challenging Lighting Conditions},
  author    = {Merlos, Juan and Harrison, Andre and Jefferson II, Darius and Adzic, Velibor and Kalva, Hari},
  booktitle = {IEEE International Conference on Image Processing (ICIP)},
  year      = {2026}
}
```

In addition to citing our paper, please also cite the original source-image datasets you use (IndoorHDRDataset2018, SYNS, UPIQ, HDR4RTT, and/or Reinhard et al.) — see the references listed under each **Source datasets** section above.

---

## Questions?

Feel free to open an issue or reach out. Hope HDRDCL is useful for your work! mlab@fau.edu
