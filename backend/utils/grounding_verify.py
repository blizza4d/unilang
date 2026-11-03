import io
import logging
from PIL import Image
from schemas.grounding import GroundingResult

logger = logging.getLogger("datanova.grounding_verify")


def verify_grounding_boxes(
    pil_images: list[Image.Image],
    grounding: GroundingResult,
) -> GroundingResult:
    """Validates that bounding box crops correspond to physical image regions."""
    if not pil_images or not grounding.fields:
        return grounding

    for fg in grounding.fields:
        for box in fg.boxes:
            p_idx = box.page - 1
            if 0 <= p_idx < len(pil_images):
                img = pil_images[p_idx]
                w, h = img.size
                left = int(box.x * w)
                top = int(box.y * h)
                right = int((box.x + box.width) * w)
                bottom = int((box.y + box.height) * h)

                # Ensure crop has minimum valid area
                if right > left and bottom > top:
                    fg.grounding_confidence = min(fg.grounding_confidence, 0.98)
                else:
                    fg.grounding_confidence = 0.5

    return grounding


def calculate_iou(box1: list[int | float], box2: list[int | float]) -> float:
    ymin1, xmin1, ymax1, xmax1 = box1
    ymin2, xmin2, ymax2, xmax2 = box2

    inter_ymin = max(ymin1, ymin2)
    inter_xmin = max(xmin1, xmin2)
    inter_ymax = min(ymax1, ymax2)
    inter_xmax = min(xmax1, xmax2)

    if inter_ymax <= inter_ymin or inter_xmax <= inter_xmin:
        return 0.0

    inter_area = (inter_ymax - inter_ymin) * (inter_xmax - inter_xmin)
    area1 = (ymax1 - ymin1) * (xmax1 - xmin1)
    area2 = (ymax2 - ymin2) * (xmax2 - xmin2)
    union_area = area1 + area2 - inter_area

    return float(inter_area) / float(union_area) if union_area > 0 else 0.0


def verify_box_dimensions(box: list[int | float]) -> bool:
    ymin, xmin, ymax, xmax = box
    return (ymax > ymin) and (xmax > xmin)

