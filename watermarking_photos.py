from pathlib import Path
from PIL import Image, ImageOps

# 1. Get user input (strips quotes if paths are dragged into the terminal)
folder_path = Path(input("Image folder path: ").strip().strip('"').strip("'"))
wm_path = Path(input("Watermark image path: ").strip().strip('"').strip("'"))
scale_input = input("Watermark width % (press Enter for 15%, or 0 for original size): ").strip()

if not folder_path.is_dir():
    print("Error: That image folder does not exist.")
    exit()

if not wm_path.is_file():
    print("Error: That watermark file does not exist.")
    exit()

try:
    scale_pct = float(scale_input) if scale_input else 15.0
    if scale_pct < 0 or scale_pct > 100:
        raise ValueError
except ValueError:
    print("Error: Enter a valid percentage between 0 and 100.")
    exit()

# 2. Collect supported images (excluding the watermark itself if in the same folder)
valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
images = sorted(
    f for f in folder_path.iterdir()
    if f.is_file()
    and f.suffix.lower() in valid_extensions
    and f.resolve() != wm_path.resolve()
)

if not images:
    print("No supported images found in that folder.")
    exit()

# 3. Prepare output folder and load watermark
output_folder = folder_path / "watermarked"
output_folder.mkdir(exist_ok=True)

watermark_orig = Image.open(wm_path).convert("RGBA")
padding = 20  # Pixels away from the bottom and right edges

# 4. Apply watermark to each image
for img_path in images:
    with Image.open(img_path) as raw_img:
        # Preserve camera/phone EXIF orientation
        base_img = ImageOps.exif_transpose(raw_img).convert("RGBA")
        img_w, img_h = base_img.size

        # Scale watermark proportionally (or keep original size if 0)
        if scale_pct > 0:
            target_w = max(1, int(img_w * (scale_pct / 100)))
            aspect_ratio = watermark_orig.height / watermark_orig.width
            target_h = max(1, int(target_w * aspect_ratio))
            watermark = watermark_orig.resize((target_w, target_h), Image.Resampling.LANCZOS)
        else:
            watermark = watermark_orig

        wm_w, wm_h = watermark.size
        position = (max(0, img_w - wm_w - padding), max(0, img_h - wm_h - padding))

        # Clean alpha compositing for transparent PNGs
        overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        overlay.paste(watermark, position)
        combined = Image.alpha_composite(base_img, overlay)

        # JPEGs do not support transparency, so convert back to RGB
        if img_path.suffix.lower() in {".jpg", ".jpeg"}:
            combined = combined.convert("RGB")

        combined.save(output_folder / img_path.name)

print(f"Done! Watermarked {len(images)} images in {output_folder}")