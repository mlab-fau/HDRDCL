#!/usr/bin/env python3
"""
Assemble HDRDCL: pair every label .json in this repo with the matching source
HDR/EXR image and write a clean output directory grouped by source dataset
and task.

Edit the three paths below or pass them on the command line.

Repo layout this script expects:
    LABELS_DIR/
        <dataset>/                 e.g. IndoorHDRDataset2018, SYNS, HDR4RTT, upiq_dataset, images
            detection/*.json
            segmentation/*.json
            (optional) <stem>.png  preview thumbnails next to the json files

Source images directory (downloaded separately):
    IMAGES_DIR/
        <dataset>/                 same names as above; HDR4RTT may have an
                                   inner images/ subfolder
            <stem>.exr | <stem>.hdr

Output:
    OUTPUT_DIR/
        <dataset>/
            detection/
                <stem>.json
                <stem>.exr|.hdr
                <stem>.png         (only if a preview was alongside the json)
            segmentation/
                ...
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURATION — set IMAGES_DIR and OUTPUT_DIR before running, OR pass them
# on the command line with --images and --out. LABELS_DIR points to this
# repo's bundled labels/ directory by default and usually doesn't need
# changing.
# ---------------------------------------------------------------------------
REPO_DIR   = Path(__file__).resolve().parent
LABELS_DIR = REPO_DIR / "labels"
BUNDLED_SOURCES_DIR = REPO_DIR / "sources"           # repo-bundled source images (e.g. the `bonus/` dataset)
IMAGES_DIR = Path("/PATH/TO/SOURCE/IMAGES")          # <-- where you downloaded the source HDR datasets
OUTPUT_DIR = Path("/PATH/TO/OUTPUT/DATASET")         # <-- where the assembled dataset will be written
# ---------------------------------------------------------------------------

LABEL_AUX_EXTS = {".png", ".jpg", ".jpeg"}
SOURCE_EXTS = {".exr", ".hdr"}


def index_dataset_sources(dataset_dir: Path) -> dict[str, list[Path]]:
    """Recursively index .exr/.hdr files in one source dataset directory."""
    index: dict[str, list[Path]] = {}
    if not dataset_dir.is_dir():
        return index
    for dp, _, files in os.walk(dataset_dir):
        for f in files:
            p = Path(dp) / f
            if p.suffix.lower() in SOURCE_EXTS:
                index.setdefault(p.stem, []).append(p)
    return index


def pick_source(candidates: list[Path]) -> Path:
    # Prefer .hdr when both .hdr and .exr exist for the same stem.
    hdrs = [c for c in candidates if c.suffix.lower() == ".hdr"]
    return hdrs[0] if hdrs else candidates[0]


def place(src: Path, dst: Path, mode: str, dry_run: bool) -> None:
    if dst.exists() or dst.is_symlink():
        return
    if dry_run:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        os.symlink(src, dst)
    elif mode == "copy":
        shutil.copy2(src, dst)
    elif mode == "hardlink":
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    else:
        raise ValueError(f"unknown mode: {mode}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--labels", type=Path, default=LABELS_DIR,
                    help=f"labels root (default: {LABELS_DIR})")
    ap.add_argument("--images", type=Path, default=IMAGES_DIR,
                    help=f"source images root (default: {IMAGES_DIR})")
    ap.add_argument("--out", type=Path, default=OUTPUT_DIR,
                    help=f"output dir (default: {OUTPUT_DIR})")
    ap.add_argument(
        "--mode",
        choices=("symlink", "copy", "hardlink"),
        default="symlink",
        help="how to place source images in the output (default: symlink)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="don't write anything; print every json -> source pairing",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="with --dry-run, only show first N pairings per dataset/task (0 = all)",
    )
    args = ap.parse_args()

    if str(args.out) == "/PATH/TO/OUTPUT/DATASET":
        print(
            "error: OUTPUT_DIR is unconfigured.\n"
            "  Either edit OUTPUT_DIR near the top of build_dataset.py,\n"
            "  or pass --out <output-dir> on the command line.",
            file=sys.stderr,
        )
        return 2
    images_dir: Path | None = args.images
    if str(images_dir) == "/PATH/TO/SOURCE/IMAGES":
        # IMAGES_DIR not configured — only the repo-bundled sources will be available.
        # Datasets that need external images will be skipped with a warning.
        images_dir = None
    if not args.labels.is_dir():
        print(f"labels dir not found: {args.labels}", file=sys.stderr)
        return 1
    if images_dir is not None and not images_dir.is_dir():
        print(f"images dir not found: {images_dir}", file=sys.stderr)
        return 1

    print(f"labels:   {args.labels}")
    print(f"bundled:  {BUNDLED_SOURCES_DIR}{'  (not present)' if not BUNDLED_SOURCES_DIR.is_dir() else ''}")
    print(f"images:   {images_dir if images_dir else '(none configured — using bundled sources only)'}")
    print(f"output:   {args.out}")
    print(f"mode:     {args.mode}{' (dry run)' if args.dry_run else ''}\n")

    per_group: dict[tuple[str, str], int] = {}
    total_matched = 0
    total_unmatched = 0
    unmatched_log: list[str] = []

    for ds_dir in sorted(p for p in args.labels.iterdir() if p.is_dir()):
        ds = ds_dir.name
        # Look for source images in: (1) the repo-bundled sources/<ds>/ dir, then
        # (2) the user's external IMAGES_DIR/<ds>/. Either is fine; both are merged
        # into a single per-dataset stem index.
        candidate_src_dirs: list[Path] = []
        bundled = BUNDLED_SOURCES_DIR / ds
        if bundled.is_dir():
            candidate_src_dirs.append(bundled)
        if images_dir is not None:
            external = images_dir / ds
            if external.is_dir():
                candidate_src_dirs.append(external)
        if not candidate_src_dirs:
            tried = [str(bundled)] + ([str(images_dir / ds)] if images_dir else [])
            print(f"[skip] {ds}: no source dir found (tried {' or '.join(tried)})")
            continue
        src_index: dict[str, list[Path]] = {}
        for d in candidate_src_dirs:
            for stem, paths in index_dataset_sources(d).items():
                src_index.setdefault(stem, []).extend(paths)

        for task_dir in sorted(p for p in ds_dir.iterdir() if p.is_dir()):
            task = task_dir.name
            jsons = sorted(p for p in task_dir.iterdir() if p.suffix.lower() == ".json")
            if not jsons:
                continue
            out_dir = args.out / ds / task
            matched = 0
            unmatched = 0
            shown = 0
            if args.dry_run:
                print(f"\n=== {ds}/{task} ===")
            for jp in jsons:
                candidates = src_index.get(jp.stem)
                if not candidates:
                    unmatched += 1
                    unmatched_log.append(f"{ds}/{task}/{jp.name}")
                    if args.dry_run:
                        print(f"  [MISS] {jp.name}  (no source under {' or '.join(str(d) for d in candidate_src_dirs)})")
                    continue
                src = pick_source(candidates)
                aux_files = [
                    jp.with_suffix(ext)
                    for ext in LABEL_AUX_EXTS
                    if jp.with_suffix(ext).exists()
                ]
                if args.dry_run and (args.limit == 0 or shown < args.limit):
                    ambig = (
                        f"  (ambiguous: {len(candidates)} sources, picked {src.suffix})"
                        if len(candidates) > 1 else ""
                    )
                    aux_note = f"  +{len(aux_files)} aux" if aux_files else ""
                    print(f"  {jp.name}{aux_note}")
                    print(f"      json    {jp}")
                    print(f"      source  {src}{ambig}")
                    for aux in aux_files:
                        print(f"      aux     {aux}")
                    shown += 1
                place(jp, out_dir / jp.name, "copy", args.dry_run)
                place(src, out_dir / src.name, args.mode, args.dry_run)
                for aux in aux_files:
                    place(aux, out_dir / aux.name, "copy", args.dry_run)
                matched += 1

            if args.dry_run and args.limit and matched > args.limit:
                print(f"  ... ({matched - args.limit} more not shown)")
            print(f"{ds}/{task}: {matched} matched, {unmatched} unmatched")
            per_group[(ds, task)] = matched
            total_matched += matched
            total_unmatched += unmatched

    print("\nBy source dataset:")
    by_ds: dict[str, dict[str, int]] = {}
    for (ds, task), n in per_group.items():
        by_ds.setdefault(ds, {})[task] = n
    for ds in sorted(by_ds):
        ds_total = sum(by_ds[ds].values())
        print(f"  {ds}/  ({ds_total} pairs)")
        for task in sorted(by_ds[ds]):
            print(f"    {task}/  {by_ds[ds][task]}")

    print(f"\nTOTAL: {total_matched} matched, {total_unmatched} unmatched")
    if unmatched_log:
        print("first unmatched:")
        for u in unmatched_log[:10]:
            print(f"  {u}")
    if args.dry_run:
        print("\n(dry run — no files were written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
