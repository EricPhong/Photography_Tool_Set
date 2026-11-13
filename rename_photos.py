import uuid
from pathlib import Path

# 1. Get user input (strips quotes if you drag-and-drop the folder into the terminal)
folder_path = Path(input("Folder path with images: ").strip().strip('"').strip("'"))
base_name = input("New base filename: ").strip()

if not folder_path.is_dir():
    print("Error: That folder path does not exist.")
    exit()

# 2. Collect and sort image files
valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
images = sorted(
    f for f in folder_path.iterdir()
    if f.is_file() and f.suffix.lower() in valid_extensions
)

# 3. Step 1: Rename to temporary names first to prevent filename collisions
temp_files = []
for img_path in images:
    temp_path = img_path.with_name(f"__temp_{uuid.uuid4().hex}{img_path.suffix}")
    img_path.rename(temp_path)
    temp_files.append(temp_path)

# 4. Step 2: Apply the final sequential names (e.g., Event_001.jpg)
for index, temp_path in enumerate(temp_files, start=1):
    new_name = f"{base_name}_{index:03d}{temp_path.suffix}"
    temp_path.rename(temp_path.with_name(new_name))

print(f"Done! Renamed {len(temp_files)} images in {folder_path}")
