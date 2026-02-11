"""
Rock/grain counting from images using computer vision.

Uses OpenCV (Otsu thresholding, morphology, connected components) with an
optional watershed step (scikit-image) to separate touching objects.
Libraries that work well for counting items in images:

- OpenCV: thresholding, morphology, connected components (this module).
- scikit-image: watershed for touching objects, label(), regionprops.
- Cellpose: deep-learning instance segmentation for blob-like objects
  (pip install cellpose) — good for irregular/overlapping grains.
- YOLO/Ultralytics: object detection, count detections (train on "rock").
- Segment Anything (SAM): generic segmentation, then count instances.
"""

import re
import base64
import numpy as np
import cv2

# Optional: watershed for separating touching rocks
try:
    from skimage.measure import label as sk_label
    from skimage.morphology import watershed
    from skimage.feature import peak_local_max
    from scipy import ndimage as ndi
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


def _decode_image(data_url_or_bytes):
    """Decode image from base64 data URL (e.g. from canvas.toDataURL()) or raw base64 bytes."""
    if isinstance(data_url_or_bytes, bytes):
        data = data_url_or_bytes
    else:
        s = data_url_or_bytes.strip()
        if s.startswith("data:"):
            match = re.match(r"data:image/[^;]+;base64,(.+)", s)
            if not match:
                raise ValueError("Invalid data URL")
            data = base64.b64decode(match.group(1))
        else:
            data = base64.b64decode(s)
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def _get_binary_mask(bgr, blur_radius=5, use_otsu=True):
    """Convert to grayscale, optional blur, Otsu threshold. Returns uint8 mask (0 or 255)."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    if blur_radius > 0:
        gray = cv2.GaussianBlur(gray, (blur_radius | 1, blur_radius | 1), 0)
    if use_otsu:
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    return mask


def _morphology_cleanup(mask, open_radius=2, close_radius=3):
    """Remove small noise (open) and fill small holes (close)."""
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_radius * 2 + 1,) * 2)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_radius * 2 + 1,) * 2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    return mask


def count_with_connected_components(mask, min_area_px=50, max_area_frac=0.4):
    """
    Count objects using OpenCV connectedComponentsWithStats.
    Filters by min_area_px and max area as fraction of image.
    """
    h, w = mask.shape[:2]
    total = h * w
    max_area_px = int(total * max_area_frac)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    count = 0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if min_area_px <= area <= max_area_px:
            count += 1
    return count


def count_with_watershed(mask, min_distance=10, min_area_px=50, max_area_frac=0.4):
    """
    Separate touching objects with watershed (scikit-image), then count.
    Uses distance transform and peak_local_max for markers.
    """
    if not SKIMAGE_AVAILABLE:
        return count_with_connected_components(mask, min_area_px, max_area_frac)
    # Distance transform (objects = white in our mask)
    dist = ndi.distance_transform_edt(mask)
    # Local maxima as markers
    coords = peak_local_max(dist, min_distance=min_distance, exclude_border=True)
    if coords.size == 0:
        return count_with_connected_components(mask, min_area_px, max_area_frac)
    markers = np.zeros_like(mask, dtype=np.int32)
    for idx, (r, c) in enumerate(coords, start=1):
        markers[r, c] = idx
    # Watershed on negative distance so basins are objects
    labels_ws = watershed(-dist, markers, mask=mask.astype(bool))
    h, w = mask.shape[:2]
    total = h * w
    max_area_px = int(total * max_area_frac)
    count = 0
    for uid in np.unique(labels_ws):
        if uid == 0:
            continue
        area = np.sum(labels_ws == uid)
        if min_area_px <= area <= max_area_px:
            count += 1
    return count


def count_rocks(
    image_input,
    *,
    blur=5,
    use_watershed=True,
    min_area_px=50,
    max_area_frac=0.4,
    watershed_min_distance=10,
):
    """
    Count rocks/grains in an image.

    image_input: base64 data URL string (e.g. from canvas.toDataURL('image/jpeg'))
                 or bytes (raw base64) or numpy BGR array.

    Returns dict: { "count": int, "method": "watershed"|"connected_components", "error": str or None }
    """
    try:
        if isinstance(image_input, np.ndarray):
            img = image_input
        else:
            img = _decode_image(image_input)
    except Exception as e:
        return {"count": 0, "method": "none", "error": str(e)}

    try:
        mask = _get_binary_mask(img, blur_radius=blur, use_otsu=True)
        mask = _morphology_cleanup(mask, open_radius=2, close_radius=3)

        if use_watershed and SKIMAGE_AVAILABLE:
            count = count_with_watershed(
                mask,
                min_distance=watershed_min_distance,
                min_area_px=min_area_px,
                max_area_frac=max_area_frac,
            )
            method = "watershed"
        else:
            count = count_with_connected_components(
                mask, min_area_px=min_area_px, max_area_frac=max_area_frac
            )
            method = "connected_components"

        return {"count": count, "method": method, "error": None}
    except Exception as e:
        return {"count": 0, "method": "none", "error": str(e)}
