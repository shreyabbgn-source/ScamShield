from PIL import Image, ImageFilter
import io
import math

def analyze_image_quality(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size
    file_size_kb = len(image_bytes) / 1024

    # Blur detection via Laplacian variance approximation
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    pixels = list(edges.getdata())
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
    sharpness_score = math.sqrt(variance)

    if sharpness_score > 15:
        blur_level = "Low"
    elif sharpness_score > 7:
        blur_level = "Medium"
    else:
        blur_level = "High"

    # Compression estimate from file size vs dimensions
    pixels_total = width * height
    bytes_per_pixel = (file_size_kb * 1024) / pixels_total if pixels_total > 0 else 0

    if bytes_per_pixel < 0.3:
        compression = "High"
    elif bytes_per_pixel < 1.0:
        compression = "Medium"
    else:
        compression = "Low"

    # Overall image quality
    if blur_level == "Low" and compression == "Low":
        quality = "High"
    elif blur_level == "High" or compression == "High":
        quality = "Low"
    else:
        quality = "Medium"

    return {
        "width": width,
        "height": height,
        "file_size_kb": round(file_size_kb, 1),
        "blur_level": blur_level,
        "compression": compression,
        "image_quality": quality,
        "sharpness_score": round(sharpness_score, 1),
    }