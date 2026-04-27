import re

from app.core.patterns import ALL_PATTERNS, MASK_CHARS, REPLACEMENTS, scan_geo
from app.services.fake_generator import fake_generator
from app.services.mapping_store import mapping_store
from app.services.model_manager import model_manager
from app.services.name_gazetteer import scan_names


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
    "DRIVER_LICENSE",
    "OMS",
}


def _merge_entities(
    ml_entities: list[dict],
    regex_entities: list[dict],
    gazetteer_entities: list[dict] | None = None,
    geo_entities: list[dict] | None = None,
) -> list[dict]:
    if gazetteer_entities is None:
        gazetteer_entities = []
    if geo_entities is None:
        geo_entities = []

    regex_spans = [(e["start"], e["end"]) for e in regex_entities]

    filtered_ml = []
    for e in ml_entities:
        dominated = False
        for rs, re_ in regex_spans:
            if _ranges_overlap(e["start"], e["end"], rs, re_):
                dominated = True
                break
        if not dominated:
            filtered_ml.append(e)

    ml_spans = [(e["start"], e["end"]) for e in filtered_ml]
    regex_ml_spans = regex_spans + ml_spans

    filtered_gaz = []
    for e in gazetteer_entities:
        dominated = False
        for rs, re_ in regex_ml_spans:
            if _ranges_overlap(e["start"], e["end"], rs, re_):
                dominated = True
                break
        if not dominated:
            filtered_gaz.append(e)

    gaz_spans = [(e["start"], e["end"]) for e in filtered_gaz]
    all_spans = regex_ml_spans + gaz_spans

    filtered_geo = []
    for e in geo_entities:
        dominated = False
        for rs, re_ in all_spans:
            if _ranges_overlap(e["start"], e["end"], rs, re_):
                dominated = True
                break
        if not dominated:
            filtered_geo.append(e)

    all_entities = regex_entities + filtered_ml + filtered_gaz + filtered_geo
    all_entities.sort(key=lambda x: x["start"])

    result = []
    for e in all_entities:
        overlaps = False
        for existing in result:
            if _ranges_overlap(e["start"], e["end"], existing["start"], existing["end"]):
                overlaps = True
                break
        if not overlaps:
            result.append(e)

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


_STREET_LEFT_CTX = {
    "ул",
    "пр",
    "проспект",
    "бульвар",
    "переулок",
    "шоссе",
    "пл",
    "площадь",
    "набережная",
    "проезд",
    "наб",
    "пер",
}


def _mark_street_entities(entities: list[dict], text: str) -> list[dict]:
    result = []
    for e in entities:
        if e["label"] == "LOC":
            inner = e["text"].lower()
            first_word = inner.split()[0].rstrip(".,") if inner.split() else ""
            if first_word in _STREET_LEFT_CTX or first_word.rstrip("еёомой"):
                root = first_word
                for prefix in _STREET_LEFT_CTX:
                    if root.startswith(prefix):
                        result.append({**e, "label": "STREET"})
                        break
                else:
                    pass
                if result and result[-1] is not e and result[-1].get("label") == "STREET":
                    continue
            before = text[: e["start"]].rstrip()
            if before:
                last_word = before.split()[-1].lower().rstrip(".,")
                if last_word in _STREET_LEFT_CTX or any(
                    last_word.startswith(p) and len(last_word) - len(p) <= 3
                    for p in _STREET_LEFT_CTX
                ):
                    result.append({**e, "label": "STREET"})
                    continue
        result.append(e)
    return result


_LOC_GAP_RE = re.compile(r"^[-\s]*(?:на[-\s]+)?$")


def _merge_adjacent_same_label(entities: list[dict], text: str) -> list[dict]:
    if not entities:
        return entities
    result = [dict(entities[0])]
    for e in entities[1:]:
        prev = result[-1]
        if e["label"] != prev["label"]:
            result.append(dict(e))
            continue
        gap = text[prev["end"] : e["start"]]
        if e["label"] == "LOC" and _LOC_GAP_RE.match(gap) and len(gap) <= 6:
            prev["end"] = e["end"]
            prev["text"] = text[prev["start"] : e["end"]]
            prev["score"] = max(prev["score"], e["score"])
            continue
        if e["start"] - prev["end"] <= 1:
            prev["end"] = e["end"]
            prev["text"] = text[prev["start"] : e["end"]]
            prev["score"] = max(prev["score"], e["score"])
            continue
        result.append(dict(e))
    return result


def depersonalize_text(text: str, mode: str = "replace") -> dict:
    fake_generator.reset()
    ml_entities = model_manager.predict(text)
    regex_entities = _regex_scan(text)
    gazetteer_entities = scan_names(text)
    geo_entities = scan_geo(text)
    entities = _merge_entities(ml_entities, regex_entities, gazetteer_entities, geo_entities)
    entities = _mark_street_entities(entities, text)
    entities.sort(key=lambda x: x["start"])
    entities = _merge_adjacent_same_label(entities, text)

    processed = _apply_mode(text, entities, mode)

    key = None
    if mode == "fake":
        reverse = fake_generator.get_reverse_mapping()
        if reverse:
            key = mapping_store.save(reverse)

    by_type = {}
    for e in entities:
        by_type[e["label"]] = by_type.get(e["label"], 0) + 1

    return {
        "original_text": text,
        "processed_text": processed,
        "entities": entities,
        "stats": {"total_entities": len(entities), "by_type": by_type},
        "key": key,
    }
