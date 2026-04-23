import re

from app.core.patterns import ALL_PATTERNS, REPLACEMENTS, MASK_CHARS
from app.services.model_manager import model_manager
from app.services.fake_generator import fake_generator


def _ranges_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


_REGEX_LABELS = {
    "PHONE",
    "EMAIL",
    "INN",
    "SNILS",
    "PASSPORT",
    "CARD",
    "DATE",
    "IP",
}


def _merge_entities(ml_entities: list[dict], regex_entities: list[dict]) -> list[dict]:
    all_entities = ml_entities + regex_entities
    all_entities.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))

    regex_spans = set()
    for e in regex_entities:
        regex_spans.add((e["start"], e["end"]))

    filtered_ml = []
    for e in ml_entities:
        dominated_by_regex = False
        for rs, re_ in regex_spans:
            if _ranges_overlap(e["start"], e["end"], rs, re_):
                dominated_by_regex = True
                break
        if not dominated_by_regex:
            filtered_ml.append(e)

    combined = regex_entities + filtered_ml
    combined.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))

    result = []
    for e in combined:
        dominated = False
        for existing in result:
            if _ranges_overlap(e["start"], e["end"], existing["start"], existing["end"]):
                existing_len = existing["end"] - existing["start"]
                current_len = e["end"] - e["start"]
                e_is_regex = e["label"] in _REGEX_LABELS
                ex_is_regex = existing["label"] in _REGEX_LABELS
                if e_is_regex and not ex_is_regex:
                    pass
                elif current_len <= existing_len:
                    dominated = True
                    break
        if not dominated:
            result_new = []
            for existing in result:
                if _ranges_overlap(e["start"], e["end"], existing["start"], existing["end"]):
                    existing_len = existing["end"] - existing["start"]
                    current_len = e["end"] - e["start"]
                    e_is_regex = e["label"] in _REGEX_LABELS
                    ex_is_regex = existing["label"] in _REGEX_LABELS
                    if e_is_regex and not ex_is_regex:
                        continue
                    if current_len > existing_len:
                        continue
                result_new.append(existing)
            result_new.append(e)
            result = result_new

    result.sort(key=lambda x: x["start"])
    return result


def _regex_scan(text: str) -> list[dict]:
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
    return entities


def _apply_mode(text: str, entities: list[dict], mode: str) -> str:
    if mode == "redact":
        for e in reversed(entities):
            text = text[: e["start"]] + "[REDACTED]" + text[e["end"] :]
        return text

    if mode == "mask":
        for e in reversed(entities):
            mask_fn = MASK_CHARS.get(e["label"])
            if mask_fn:
                masked = mask_fn(re.match(r".*", e["text"]))
                text = text[: e["start"]] + masked + text[e["end"] :]
            else:
                text = text[: e["start"]] + re.sub(r"\S", "X", e["text"]) + text[e["end"] :]
        return text

    if mode == "fake":
        for e in reversed(entities):
            replacement = fake_generator.replace(e["label"], e["text"])
            text = text[: e["start"]] + replacement + text[e["end"] :]
        return text

    for e in reversed(entities):
        replacement = REPLACEMENTS.get(e["label"], f"[{e['label']}]")
        text = text[: e["start"]] + replacement + text[e["end"] :]
    return text


def depersonalize_text(text: str, mode: str = "replace") -> dict:
    fake_generator.reset()
    ml_entities = model_manager.predict(text)
    regex_entities = _regex_scan(text)
    entities = _merge_entities(ml_entities, regex_entities)

    processed = _apply_mode(text, entities, mode)

    by_type = {}
    for e in entities:
        by_type[e["label"]] = by_type.get(e["label"], 0) + 1

    return {
        "original_text": text,
        "processed_text": processed,
        "entities": entities,
        "stats": {"total_entities": len(entities), "by_type": by_type},
    }
