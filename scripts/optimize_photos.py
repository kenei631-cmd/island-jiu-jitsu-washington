"""Optimize a supplied photo ZIP; keep all original files untouched and unpublished.

Usage: python3 scripts/optimize_photos.py /path/to/archive.zip
Requires Pillow with WebP support. Builds content-hashed, metadata-free WebP
variants and a filename/URL inventory. No network or AI services are used.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageOps, ImageCms
import argparse
import csv
import hashlib
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "assets/photos/william-wallace"
ORIGIN = "https://island-jiu-jitsu-washington.netlify.app"
SIZES = {"thumbnail": (320, 76), "medium": (960, 80), "large": (1920, 84)}
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def optimize(zip_path, source_member, digest, aliases, original_bytes):
    with ZipFile(zip_path) as archive:
        data = archive.read(source_member)
    with Image.open(io.BytesIO(data)) as original:
        photo = ImageOps.exif_transpose(original)
        profile = photo.info.get("icc_profile")
        if profile:
            try:
                alpha = photo.getchannel("A") if photo.mode == "RGBA" else None
                photo = ImageCms.profileToProfile(
                    photo, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                    ImageCms.createProfile("sRGB"), outputMode="RGB"
                )
                if alpha is not None:
                    photo.putalpha(alpha)
            except (ImageCms.PyCMSError, OSError, ValueError):
                photo = photo.convert("RGBA" if photo.mode == "RGBA" else "RGB")
        elif photo.mode not in ("RGB", "RGBA"):
            photo = photo.convert("RGBA" if "transparency" in photo.info else "RGB")
        photo.load()
        # Rebuild from pixels only so source EXIF, XMP, GPS and ICC are not saved.
        clean = Image.frombytes(photo.mode, photo.size, photo.tobytes())
    width, height = clean.size
    stem = Path(aliases[0]).stem
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") or "photo"
    slug = "ijj-washington-" + slug[:65] + "-" + digest[:10]
    record = {
        "id": "ww-" + digest[:12], "name": stem, "sourceFiles": aliases,
        "sourceSHA256": digest, "sourceWidth": width, "sourceHeight": height,
        "sourceBytes": original_bytes,
        "orientation": "landscape" if width > height else "portrait" if height > width else "square",
        "variants": {},
    }
    for variant, (long_side, quality) in SIZES.items():
        image = clean.copy()
        image.thumbnail((long_side, long_side), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=quality, method=6)
        encoded = buffer.getvalue()
        encoded_hash = hashlib.sha256(encoded).hexdigest()
        filename = f"{slug}-{variant}-{encoded_hash[:12]}.webp"
        path = DESTINATION / filename
        path.write_bytes(encoded)
        record["variants"][variant] = {
            "path": str(path.relative_to(ROOT)), "width": image.width,
            "height": image.height, "bytes": len(encoded), "sha256": encoded_hash,
        }
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not args.archive.is_file():
        raise SystemExit("Photo archive not found")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    groups, photo_count, original_total, excluded = {}, 0, 0, []
    with ZipFile(args.archive) as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename.casefold()):
            if info.is_dir() or info.filename.startswith("__MACOSX/"):
                continue
            if Path(info.filename).suffix.lower() not in PHOTO_EXTENSIONS:
                excluded.append({"filename": Path(info.filename).name, "bytes": info.file_size})
                continue
            data = archive.read(info)
            digest = hashlib.sha256(data).hexdigest()
            photo_count += 1
            original_total += info.file_size
            if digest in groups:
                groups[digest]["aliases"].append(Path(info.filename).name)
            else:
                groups[digest] = {"member": info.filename, "aliases": [Path(info.filename).name], "bytes": info.file_size}
    print(f"Found {photo_count} photos: {len(groups)} unique and {photo_count-len(groups)} duplicates; {len(excluded)} non-photo files.", flush=True)
    photos, failures = [], []
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
        futures = {
            executor.submit(optimize, args.archive, group["member"], digest, group["aliases"], group["bytes"]): group["member"]
            for digest, group in groups.items()
        }
        for index, future in enumerate(as_completed(futures), 1):
            try:
                photos.append(future.result())
            except Exception as error:
                failures.append({"filename": futures[future], "error": str(error)})
            if index % 20 == 0 or index == len(futures):
                print(f"Optimized {index}/{len(futures)} photos; errors: {len(failures)}", flush=True)
    if failures:
        raise SystemExit("Import stopped before catalog publication: " + json.dumps(failures))
    photos.sort(key=lambda photo: photo["name"].casefold())
    summary = {
        "sourcePhotoCount": photo_count, "uniquePhotoCount": len(photos),
        "duplicateCount": photo_count-len(photos), "excludedFiles": excluded,
        "originalPhotoBytes": original_total,
        "uniqueOriginalBytes": sum(photo["sourceBytes"] for photo in photos),
        "optimizedTotalBytes": sum(v["bytes"] for p in photos for v in p["variants"].values()),
        "largeTotalBytes": sum(p["variants"]["large"]["bytes"] for p in photos),
        "variants": {key: {"maxLongSide": size, "quality": quality} for key, (size, quality) in SIZES.items()},
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "preservesFullFrame": True, "locationMetadataRemoved": True,
        "publicOrigin": ORIGIN,
    }
    catalog = {"version": 1, "collection": "William Wallace photo upload", "summary": summary, "photos": photos}
    catalog_dir = DESTINATION.parent
    (catalog_dir / "library.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    with (catalog_dir / "library.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["photo_id", "original_filenames", "orientation", "source_width", "source_height", "variant", "width", "height", "bytes", "netlify_url"])
        for photo in photos:
            for variant, value in photo["variants"].items():
                writer.writerow([photo["id"], " | ".join(photo["sourceFiles"]), photo["orientation"], photo["sourceWidth"], photo["sourceHeight"], variant, value["width"], value["height"], value["bytes"], ORIGIN + "/" + value["path"]])
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
