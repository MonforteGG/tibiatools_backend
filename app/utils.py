import cv2
import numpy as np
import os
import logging
from collections import defaultdict

from app.item_data import ITEM_DATA

logger = logging.getLogger(__name__)

# Constants
TARGET_WIDTH = 1920
THRESHOLD = 0.7
NMS_DISTANCE = 20
COLORS = {
    "blue": (255, 99, 71),
    "green": (0, 255, 0),
    "rashid": (7, 111, 169)
}


def format_loot_data(detected_items: dict) -> dict:
    """
    Transform detected items into structured loot data.
    """
    formatted_data = {}
    for filename, quantity in detected_items.items():
        item_info = ITEM_DATA.get(filename)
        if item_info:
            formatted_data[item_info["name"]] = {
                "price": item_info["price"],
                "quantity": quantity,
                "category": item_info["category"]
            }
        else:
            # Optional: Handle items not found in ITEM_DATA
            formatted_data[filename] = {
                "price": 0,
                "quantity": quantity,
                "category": "unknown"
            }
    return formatted_data


# Load reference images
def load_reference_images():
    categories = {
        "blue": [],
        "green": [],
        "rashid": []
    }

    for color in categories.keys():
        folder_path = os.path.join('assets', color.capitalize())
        if not os.path.isdir(folder_path):
            logger.warning(f"Folder {folder_path} does not exist.")
            continue
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if img.shape[-1] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                categories[color].append((file_name, img))  # ⚡ Guardamos (nombre, imagen)
            else:
                logger.warning(f"Failed to load image: {file_path}")

    logger.info("Reference images loaded successfully.")
    return categories

REFERENCE_IMAGES = load_reference_images()

def is_far_enough(existing_boxes, new_box, min_distance):
    """Check if new_box is far enough from existing_boxes."""
    for (x, y) in existing_boxes:
        if np.hypot(x - new_box[0], y - new_box[1]) < min_distance:
            return False
    return True


def process_image(image_bytes: bytes):
    """Process uploaded image to detect loot items and count them."""
    np_array = np.frombuffer(image_bytes, np.uint8)
    bp_img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if bp_img is None:
        logger.error("Failed to decode uploaded image.")
        raise ValueError("Invalid image data.")

    # 1. Resize to standard width
    if bp_img.shape[1] != TARGET_WIDTH:
        ratio = TARGET_WIDTH / float(bp_img.shape[1])
        new_height = int(bp_img.shape[0] * ratio)
        bp_img = cv2.resize(bp_img, (TARGET_WIDTH, new_height))
        logger.info(f"Image resized to {TARGET_WIDTH}x{new_height}")

    # 2. Crop the image to first 352px width
    crop_width = 352
    if bp_img.shape[1] >= crop_width:
        bp_img = bp_img[:, :crop_width]  # Keep all rows, only first 352 columns
        logger.info(f"Image cropped to {crop_width}px width.")
    else:
        logger.warning(f"Image width {bp_img.shape[1]} is less than {crop_width}px. Skipping cropping.")

    logger.info("Starting template matching...")

    detection_counter = defaultdict(int)

    for category_name, images_list in REFERENCE_IMAGES.items():
        color = COLORS[category_name]
        for filename, template in images_list:
            tH, tW = template.shape[:2]

            if bp_img.shape[0] < tH or bp_img.shape[1] < tW:
                continue

            result = cv2.matchTemplate(bp_img, template, cv2.TM_CCOEFF_NORMED)
            yloc, xloc = np.where(result >= THRESHOLD)
            scores = result[yloc, xloc]

            matches = sorted(zip(scores, xloc, yloc), reverse=True)

            accepted = []

            for score, x, y in matches:
                if is_far_enough(accepted, (x, y), NMS_DISTANCE):
                    accepted.append((x, y))

                    # Draw only rectangle
                    cv2.rectangle(bp_img, (x, y), (x + tW, y + tH), color, 2)

                    # Count detection by asset name
                    detection_counter[filename] += 1

    logger.info(f"Detection completed. Total unique items: {len(detection_counter)}")
    formatted_response = format_loot_data(detection_counter)

    return bp_img, dict(formatted_response)

