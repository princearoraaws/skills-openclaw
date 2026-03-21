#!/usr/bin/env bash
set -euo pipefail

# blur — Image Blur & Privacy Mask Tool
# Version: 1.0.0
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

DATA_DIR="${HOME}/.blur"
DATA_FILE="${DATA_DIR}/data.jsonl"
CONFIG_FILE="${DATA_DIR}/config.json"
OUTPUT_DIR="${DATA_DIR}/output"
ORIGINALS_DIR="${DATA_DIR}/originals"

mkdir -p "${DATA_DIR}" "${OUTPUT_DIR}" "${ORIGINALS_DIR}"
touch "${DATA_FILE}"

if [ ! -f "${CONFIG_FILE}" ]; then
  echo '{"default_radius": 10, "default_type": "gaussian", "preserve_originals": true, "output_quality": 95}' > "${CONFIG_FILE}"
fi

COMMAND="${1:-help}"

case "${COMMAND}" in

  apply)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime, shutil

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
output_dir = os.environ.get("OUTPUT_DIR", os.path.expanduser("~/.blur/output"))
originals_dir = os.environ.get("ORIGINALS_DIR", os.path.expanduser("~/.blur/originals"))
input_path = os.environ.get("BLUR_INPUT", "")
output_path = os.environ.get("BLUR_OUTPUT", "")
radius = int(os.environ.get("BLUR_RADIUS", "10"))
blur_type = os.environ.get("BLUR_TYPE", "gaussian")

if not input_path:
    print(json.dumps({"status": "error", "message": "BLUR_INPUT is required"}), file=sys.stderr)
    sys.exit(2)

if not os.path.exists(input_path):
    print(json.dumps({"status": "error", "message": f"Image not found: {input_path}"}), file=sys.stderr)
    sys.exit(3)

try:
    from PIL import Image, ImageFilter
except ImportError:
    print(json.dumps({"status": "error", "message": "Pillow not installed. Run: pip3 install Pillow"}), file=sys.stderr)
    sys.exit(4)

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
blur_id = f"blur_{ts}_{short_id}"

if not output_path:
    base, ext = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(output_dir, f"{base}_blurred_{short_id}{ext}")

# Save original for undo
original_backup = os.path.join(originals_dir, f"{blur_id}_{os.path.basename(input_path)}")
shutil.copy2(input_path, original_backup)

img = Image.open(input_path)
original_size = img.size
original_mode = img.mode

if blur_type == "gaussian":
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
elif blur_type == "box":
    blurred = img.filter(ImageFilter.BoxBlur(radius=radius))
elif blur_type == "motion":
    kernel_size = max(3, radius)
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = [0] * (kernel_size * kernel_size)
    mid = kernel_size // 2
    for i in range(kernel_size):
        kernel[mid * kernel_size + i] = 1.0 / kernel_size
    blurred = img.filter(ImageFilter.Kernel(size=(kernel_size, kernel_size), kernel=kernel))
else:
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))

blurred.save(output_path, quality=95)
output_size = os.path.getsize(output_path)

record = {
    "id": blur_id,
    "input": input_path,
    "output": output_path,
    "original_backup": original_backup,
    "blur_type": blur_type,
    "radius": radius,
    "image_size": list(original_size),
    "image_mode": original_mode,
    "output_size_bytes": output_size,
    "command": "apply",
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "apply", "data": record}, indent=2))
PYEOF
    ;;

  face)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime, shutil

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
output_dir = os.environ.get("OUTPUT_DIR", os.path.expanduser("~/.blur/output"))
originals_dir = os.environ.get("ORIGINALS_DIR", os.path.expanduser("~/.blur/originals"))
input_path = os.environ.get("BLUR_INPUT", "")
output_path = os.environ.get("BLUR_OUTPUT", "")
radius = int(os.environ.get("BLUR_RADIUS", "20"))

if not input_path:
    print(json.dumps({"status": "error", "message": "BLUR_INPUT is required"}), file=sys.stderr)
    sys.exit(2)

if not os.path.exists(input_path):
    print(json.dumps({"status": "error", "message": f"Image not found: {input_path}"}), file=sys.stderr)
    sys.exit(3)

try:
    from PIL import Image, ImageFilter, ImageDraw
except ImportError:
    print(json.dumps({"status": "error", "message": "Pillow not installed. Run: pip3 install Pillow"}), file=sys.stderr)
    sys.exit(4)

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
blur_id = f"face_{ts}_{short_id}"

if not output_path:
    base, ext = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(output_dir, f"{base}_face_blurred_{short_id}{ext}")

original_backup = os.path.join(originals_dir, f"{blur_id}_{os.path.basename(input_path)}")
shutil.copy2(input_path, original_backup)

img = Image.open(input_path)

# Simple skin-tone based face region detection (heuristic)
# For production, use face_recognition or opencv
# Here we apply a general heuristic: detect large contiguous light regions
width, height = img.size
faces_detected = []

# Divide image into grid and look for face-like regions
grid_size = min(width, height) // 4
if grid_size > 50:
    for y in range(0, height - grid_size, grid_size // 2):
        for x in range(0, width - grid_size, grid_size // 2):
            region = img.crop((x, y, x + grid_size, y + grid_size))
            pixels = list(region.getdata())
            if len(pixels) > 0 and len(pixels[0]) >= 3:
                avg_r = sum(p[0] for p in pixels) / len(pixels)
                avg_g = sum(p[1] for p in pixels) / len(pixels)
                avg_b = sum(p[2] for p in pixels) / len(pixels)
                # Rough skin tone detection
                if 80 < avg_r < 240 and 50 < avg_g < 200 and 30 < avg_b < 180:
                    if avg_r > avg_g > avg_b:
                        faces_detected.append((x, y, grid_size, grid_size))

# Blur detected face regions
result = img.copy()
for (fx, fy, fw, fh) in faces_detected[:10]:
    face_region = result.crop((fx, fy, fx + fw, fy + fh))
    face_blurred = face_region.filter(ImageFilter.GaussianBlur(radius=radius))
    result.paste(face_blurred, (fx, fy))

result.save(output_path, quality=95)

record = {
    "id": blur_id,
    "input": input_path,
    "output": output_path,
    "original_backup": original_backup,
    "blur_type": "face_detection",
    "radius": radius,
    "faces_detected": len(faces_detected),
    "face_regions": faces_detected[:10],
    "command": "face",
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "face", "data": record}, indent=2))
PYEOF
    ;;

  region)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime, shutil

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
output_dir = os.environ.get("OUTPUT_DIR", os.path.expanduser("~/.blur/output"))
originals_dir = os.environ.get("ORIGINALS_DIR", os.path.expanduser("~/.blur/originals"))
input_path = os.environ.get("BLUR_INPUT", "")
output_path = os.environ.get("BLUR_OUTPUT", "")
radius = int(os.environ.get("BLUR_RADIUS", "10"))
region_str = os.environ.get("BLUR_REGION", "")

if not input_path:
    print(json.dumps({"status": "error", "message": "BLUR_INPUT is required"}), file=sys.stderr)
    sys.exit(2)

if not region_str:
    print(json.dumps({"status": "error", "message": "BLUR_REGION is required (format: x,y,width,height)"}), file=sys.stderr)
    sys.exit(2)

if not os.path.exists(input_path):
    print(json.dumps({"status": "error", "message": f"Image not found: {input_path}"}), file=sys.stderr)
    sys.exit(3)

try:
    from PIL import Image, ImageFilter
except ImportError:
    print(json.dumps({"status": "error", "message": "Pillow not installed"}), file=sys.stderr)
    sys.exit(4)

try:
    parts = [int(x.strip()) for x in region_str.split(",")]
    rx, ry, rw, rh = parts[0], parts[1], parts[2], parts[3]
except (ValueError, IndexError):
    print(json.dumps({"status": "error", "message": "Invalid BLUR_REGION format. Use: x,y,width,height"}), file=sys.stderr)
    sys.exit(1)

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
blur_id = f"region_{ts}_{short_id}"

if not output_path:
    base, ext = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(output_dir, f"{base}_region_blurred_{short_id}{ext}")

original_backup = os.path.join(originals_dir, f"{blur_id}_{os.path.basename(input_path)}")
shutil.copy2(input_path, original_backup)

img = Image.open(input_path)
region_box = (rx, ry, rx + rw, ry + rh)
region_crop = img.crop(region_box)
blurred_region = region_crop.filter(ImageFilter.GaussianBlur(radius=radius))
img.paste(blurred_region, region_box)
img.save(output_path, quality=95)

record = {
    "id": blur_id,
    "input": input_path,
    "output": output_path,
    "original_backup": original_backup,
    "blur_type": "region",
    "radius": radius,
    "region": {"x": rx, "y": ry, "width": rw, "height": rh},
    "command": "region",
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "region", "data": record}, indent=2))
PYEOF
    ;;

  batch)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
output_dir = os.environ.get("OUTPUT_DIR", os.path.expanduser("~/.blur/output"))
blur_dir = os.environ.get("BLUR_DIR", "")
radius = int(os.environ.get("BLUR_RADIUS", "10"))
blur_type = os.environ.get("BLUR_TYPE", "gaussian")

if not blur_dir:
    print(json.dumps({"status": "error", "message": "BLUR_DIR is required"}), file=sys.stderr)
    sys.exit(2)

if not os.path.isdir(blur_dir):
    print(json.dumps({"status": "error", "message": f"Directory not found: {blur_dir}"}), file=sys.stderr)
    sys.exit(3)

try:
    from PIL import Image, ImageFilter
except ImportError:
    print(json.dumps({"status": "error", "message": "Pillow not installed"}), file=sys.stderr)
    sys.exit(4)

extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
files = [f for f in os.listdir(blur_dir) if os.path.splitext(f)[1].lower() in extensions]

processed = []
errors = []

for fname in files:
    input_path = os.path.join(blur_dir, fname)
    short_id = uuid.uuid4().hex[:8]
    base, ext = os.path.splitext(fname)
    output_path = os.path.join(output_dir, f"{base}_blurred_{short_id}{ext}")

    try:
        img = Image.open(input_path)
        if blur_type == "gaussian":
            blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        elif blur_type == "box":
            blurred = img.filter(ImageFilter.BoxBlur(radius=radius))
        else:
            blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        blurred.save(output_path, quality=95)

        record = {
            "id": f"batch_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{short_id}",
            "input": input_path,
            "output": output_path,
            "blur_type": blur_type,
            "radius": radius,
            "command": "batch",
            "created_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
        with open(data_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        processed.append(fname)
    except Exception as e:
        errors.append({"file": fname, "error": str(e)})

print(json.dumps({
    "status": "success",
    "command": "batch",
    "data": {
        "processed": len(processed),
        "errors": len(errors),
        "processed_files": processed,
        "error_details": errors,
        "output_dir": output_dir
    }
}, indent=2))
PYEOF
    ;;

  preview)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

output_dir = os.environ.get("OUTPUT_DIR", os.path.expanduser("~/.blur/output"))
input_path = os.environ.get("BLUR_INPUT", "")
radius = int(os.environ.get("BLUR_RADIUS", "10"))
blur_type = os.environ.get("BLUR_TYPE", "gaussian")

if not input_path:
    print(json.dumps({"status": "error", "message": "BLUR_INPUT is required"}), file=sys.stderr)
    sys.exit(2)

if not os.path.exists(input_path):
    print(json.dumps({"status": "error", "message": f"Image not found: {input_path}"}), file=sys.stderr)
    sys.exit(3)

try:
    from PIL import Image, ImageFilter
except ImportError:
    print(json.dumps({"status": "error", "message": "Pillow not installed"}), file=sys.stderr)
    sys.exit(4)

short_id = uuid.uuid4().hex[:8]
base, ext = os.path.splitext(os.path.basename(input_path))
preview_path = os.path.join(output_dir, f"{base}_preview_{short_id}{ext}")

img = Image.open(input_path)
# Create low-res preview
max_size = (400, 400)
img.thumbnail(max_size, Image.LANCZOS)

if blur_type == "gaussian":
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
elif blur_type == "box":
    blurred = img.filter(ImageFilter.BoxBlur(radius=radius))
else:
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))

blurred.save(preview_path, quality=80)

print(json.dumps({
    "status": "success",
    "command": "preview",
    "data": {
        "input": input_path,
        "preview": preview_path,
        "preview_size": list(blurred.size),
        "blur_type": blur_type,
        "radius": radius
    }
}, indent=2))
PYEOF
    ;;

  undo)
    python3 << 'PYEOF'
import os, sys, json, shutil

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
blur_id = os.environ.get("BLUR_ID", "")

if not blur_id:
    print(json.dumps({"status": "error", "message": "BLUR_ID is required"}), file=sys.stderr)
    sys.exit(2)

records = []
target = None
with open(data_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        records.append(entry)
        if entry.get("id") == blur_id:
            target = entry

if not target:
    print(json.dumps({"status": "error", "message": f"Record not found: {blur_id}"}), file=sys.stderr)
    sys.exit(3)

original = target.get("original_backup", "")
output = target.get("output", "")
input_file = target.get("input", "")

if original and os.path.exists(original):
    if output and os.path.exists(output):
        os.remove(output)
    shutil.copy2(original, input_file)
    os.remove(original)

    remaining = [r for r in records if r.get("id") != blur_id]
    with open(data_file, "w") as f:
        for r in remaining:
            f.write(json.dumps(r) + "\n")

    print(json.dumps({
        "status": "success",
        "command": "undo",
        "data": {"id": blur_id, "restored": input_file, "output_removed": output}
    }, indent=2))
else:
    print(json.dumps({"status": "error", "message": "Original backup not found, cannot undo"}), file=sys.stderr)
    sys.exit(3)
PYEOF
    ;;

  config)
    python3 << 'PYEOF'
import os, sys, json

config_file = os.environ.get("CONFIG_FILE", os.path.expanduser("~/.blur/config.json"))
key = os.environ.get("BLUR_KEY", "")
value = os.environ.get("BLUR_VALUE", "")

config = {}
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

if key and value:
    try:
        config[key] = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        config[key] = value
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

print(json.dumps({"status": "success", "command": "config", "data": config}, indent=2))
PYEOF
    ;;

  export)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
fmt = os.environ.get("BLUR_FORMAT", "json")

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

if fmt == "csv":
    print("id,input,output,blur_type,radius,command,created_at")
    for r in records:
        print(f"{r.get('id','')},{r.get('input','')},{r.get('output','')},{r.get('blur_type','')},{r.get('radius','')},{r.get('command','')},{r.get('created_at','')}")
else:
    print(json.dumps({
        "status": "success",
        "command": "export",
        "data": {"format": fmt, "count": len(records), "records": records}
    }, indent=2))
PYEOF
    ;;

  list)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

print(json.dumps({
    "status": "success",
    "command": "list",
    "data": {"count": len(records), "records": records}
}, indent=2))
PYEOF
    ;;

  status)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.blur/data.jsonl"))
output_dir = os.environ.get("OUTPUT_DIR", os.path.expanduser("~/.blur/output"))

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

by_cmd = {}
for r in records:
    cmd = r.get("command", "unknown")
    by_cmd[cmd] = by_cmd.get(cmd, 0) + 1

output_files = os.listdir(output_dir) if os.path.exists(output_dir) else []
total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in output_files if os.path.isfile(os.path.join(output_dir, f)))

print(json.dumps({
    "status": "success",
    "command": "status",
    "data": {
        "total_processed": len(records),
        "by_command": by_cmd,
        "output_files": len(output_files),
        "total_output_size_mb": round(total_size / (1024*1024), 2),
        "data_file": data_file
    }
}, indent=2))
PYEOF
    ;;

  help)
    cat << 'HELPEOF'
blur — Image Blur & Privacy Mask Tool v1.0.0

Usage: scripts/script.sh <command>

Commands:
  apply     Apply blur to entire image (BLUR_INPUT, BLUR_RADIUS, BLUR_TYPE)
  face      Detect and blur faces (BLUR_INPUT)
  region    Blur specific region (BLUR_INPUT, BLUR_REGION=x,y,w,h)
  batch     Process directory of images (BLUR_DIR)
  preview   Generate low-res blur preview (BLUR_INPUT)
  undo      Revert a blur operation (BLUR_ID)
  config    View/update config (BLUR_KEY, BLUR_VALUE)
  export    Export history (BLUR_FORMAT: json|csv)
  list      List all processed images
  status    Show processing statistics
  help      Show this help message
  version   Show version

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
HELPEOF
    ;;

  version)
    echo '{"name": "blur", "version": "1.0.0", "author": "BytesAgain"}'
    ;;

  *)
    echo "Unknown command: ${COMMAND}" >&2
    echo "Run 'scripts/script.sh help' for usage." >&2
    exit 1
    ;;
esac
