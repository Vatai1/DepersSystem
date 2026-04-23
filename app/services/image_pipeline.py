import tempfile
import os

from PIL import Image, ImageFilter
import cv2

from app.core import logger


def _blur_regions(image_path: str, regions: list[dict], mode: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Cannot read image")

    for r in regions:
        x1, y1, x2, y2 = r["bbox"]
        h, w = y2 - y1, x2 - x1
        if h <= 0 or w <= 0:
            continue
        roi = img[y1:y2, x1:x2]
        if mode == "redact":
            roi[:] = 0
        else:
            roi = cv2.GaussianBlur(roi, (51, 51), 30)
            img[y1:y2, x1:x2] = roi

    out = image_path.replace(os.path.splitext(image_path)[1], "_depersonalized.png")
    cv2.imwrite(out, img)
    return out


def process_image(
    image_path: str, ocr_reader, entities: list[dict], mode: str = "replace"
) -> tuple[str, list[dict]]:
    results = ocr_reader.readtext(image_path)
    all_entities = []

    for detection, text, confidence in results:
        det = _detect_pii_text(text)
        if det["entities"]:
            x1 = int(min(p[0] for p in detection))
            y1 = int(min(p[1] for p in detection))
            x2 = int(max(p[0] for p in detection))
            y2 = int(max(p[1] for p in detection))
            for e in det["entities"]:
                all_entities.append({**e, "bbox": [x1, y1, x2, y2]})

    regions = [{"bbox": e["bbox"]} for e in all_entities]
    out = _blur_regions(image_path, regions, mode)
    return out, all_entities


def _detect_pii_text(text: str) -> dict:
    from app.core.patterns import ALL_PATTERNS

    entities = []
    for label, pattern in ALL_PATTERNS.items():
        for m in pattern.finditer(text):
            entities.append(
                {
                    "text": m.group(),
                    "label": label,
                    "start": m.start(),
                    "end": m.end(),
                    "score": 1.0,
                }
            )
    return {"entities": entities}
