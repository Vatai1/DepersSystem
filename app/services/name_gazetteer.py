import re

from app.data.names_gazetteer import (
    FIRST_NAMES_F,
    FIRST_NAMES_M,
    FOREIGN_FIRST_NAMES,
    FOREIGN_SURNAMES,
    GEO_STOPWORDS,
    NAME_TRIGGER_WORDS,
    NON_NAME_WORDS,
    PATRONYMICS_F,
    PATRONYMICS_M,
    SURNAME_FEMALE_ENDINGS,
    SURNAME_MALE_ENDINGS,
    SURNAMES_F,
    SURNAMES_M,
)

_SURNAMES_LOWER = {s.lower() for s in SURNAMES_M + SURNAMES_F + FOREIGN_SURNAMES}
_FIRST_NAMES_LOWER = {n.lower() for n in FIRST_NAMES_M + FIRST_NAMES_F + FOREIGN_FIRST_NAMES}
_PATRONYMICS_LOWER = {p.lower() for p in PATRONYMICS_M + PATRONYMICS_F}
_GEO_LOWER = {g.lower() for g in GEO_STOPWORDS}
_FOREIGN_SURNAMES_LOWER = {s.lower() for s in FOREIGN_SURNAMES}

_WORD_RE = re.compile(r"[А-ЯЁA-Z][а-яёa-zA-Z\-']+")


def _is_capitalized(word: str) -> bool:
    return bool(word) and word[0].isupper() and not word.isupper()


def _looks_like_surname(word: str) -> bool:
    w = word.lower().rstrip(".,:;")
    if w in _SURNAMES_LOWER:
        return True
    if w in _FOREIGN_SURNAMES_LOWER:
        return True
    if w.endswith("ович") or w.endswith("евич") or w.endswith("ична"):
        return False
    for ending in sorted(SURNAME_MALE_ENDINGS + SURNAME_FEMALE_ENDINGS, key=len, reverse=True):
        if w.endswith(ending) and len(w) > len(ending) + 2:
            return True
    return False


def _looks_like_patronymic(word: str) -> bool:
    w = word.lower().rstrip(".,:;")
    if w in _PATRONYMICS_LOWER:
        return True
    if w.endswith("ич") and len(w) > 5:
        return True
    if (w.endswith("овна") or w.endswith("евна") or w.endswith("ична")) and len(w) > 6:
        return True
    return False


def _looks_like_firstname(word: str) -> bool:
    w = word.lower().rstrip(".,:;")
    if w in _FIRST_NAMES_LOWER:
        return True
    return False


def _is_geo(word: str) -> bool:
    w = word.lower().rstrip(".,:;")
    return w in _GEO_LOWER


def _classify_word(word: str) -> str:
    w = word.lower().rstrip(".,:;")
    if w in NON_NAME_WORDS:
        return "skip"
    if _is_geo(word):
        return "geo"
    if _looks_like_patronymic(word):
        return "patronymic"
    if _looks_like_firstname(word):
        return "firstname"
    if _looks_like_surname(word):
        return "surname"
    return "unknown"


def scan_names(text: str) -> list[dict]:
    words_with_pos = []
    for m in _WORD_RE.finditer(text):
        word = m.group()
        if not _is_capitalized(word):
            continue
        w_lower = word.lower().rstrip(".,:;")
        if w_lower in NON_NAME_WORDS:
            continue
        if _is_geo(word) and not _looks_like_surname(word) and not _looks_like_firstname(word):
            continue
        if len(word) < 2:
            continue
        words_with_pos.append(
            {
                "text": word,
                "start": m.start(),
                "end": m.end(),
                "cls": _classify_word(word),
            }
        )

    if not words_with_pos:
        return []

    words_with_pos = _apply_trigger_context(text, words_with_pos)
    groups = _group_consecutive(words_with_pos, text)
    return _extract_name_entities(groups, text)


def _apply_trigger_context(text: str, words: list[dict]) -> list[dict]:
    trigger_positions = []
    for m in re.finditer(
        r"\b(" + "|".join(re.escape(t) for t in NAME_TRIGGER_WORDS) + r")\b", text, re.IGNORECASE
    ):
        trigger_positions.append(m.end())

    if not trigger_positions:
        return words

    for w in words:
        if w["cls"] == "unknown":
            for tp in trigger_positions:
                gap = text[tp : w["start"]].strip()
                if gap == "" or gap == " ":
                    w["cls"] = "surname"
                    break

    return words


def _group_consecutive(words: list[dict], text: str) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current: list[dict] = [words[0]]

    for i in range(1, len(words)):
        prev = current[-1]
        curr = words[i]
        gap_text = text[prev["end"] : curr["start"]].strip()

        if gap_text in ("", " ", ". ", ", "):
            current.append(curr)
        else:
            groups.append(current)
            current = [curr]

    if current:
        groups.append(current)
    return groups


def _is_name_group(group: list[dict]) -> bool:
    has_name_part = any(w["cls"] in ("surname", "firstname", "patronymic") for w in group)
    if not has_name_part:
        return False

    non_name = sum(1 for w in group if w["cls"] in ("skip", "geo", "unknown"))
    name_parts = sum(1 for w in group if w["cls"] in ("surname", "firstname", "patronymic"))

    if non_name > name_parts:
        return False

    return True


_NAME_CONTEXT_STOPS = {
    "карта",
    "карты",
    "карту",
    "телефон",
    "телефоны",
    "email",
    "почта",
    "паспорт",
    "серия",
    "номер",
    "инн",
    "снилс",
    "огрн",
    "бик",
    "адрес",
    "дом",
    "квартира",
    "документ",
    "договор",
    "счёт",
    "счет",
    "полис",
    "страховой",
    "поликлиника",
    "больница",
    "аптека",
    "обратился",
    "обратилась",
    "проживающий",
    "проживающая",
    "работает",
    "работала",
    "учится",
    "учился",
    "ул",
    "пр",
    "проспект",
    "бульвар",
    "переулок",
    "шоссе",
    "пл",
    "площадь",
    "набережная",
    "район",
    "область",
}

_STREET_PREFIXES = {
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


def _extract_name_entities(groups: list[list[dict]], text: str) -> list[dict]:
    entities = []
    for group in groups:
        if not _is_name_group(group):
            for w in group:
                if w["cls"] in ("surname", "firstname", "patronymic"):
                    if _is_suspicious_single(w, text):
                        continue
                    entities.append(
                        {
                            "text": w["text"],
                            "label": "PER",
                            "start": w["start"],
                            "end": w["end"],
                            "score": 0.6,
                            "source": "gazetteer",
                        }
                    )
            continue

        start = group[0]["start"]
        end = group[-1]["end"]
        full_text = text[start:end]

        parts = [w for w in group if w["cls"] not in ("skip", "geo")]
        if not parts:
            continue

        name_classes = [w["cls"] for w in parts]
        has_surname = "surname" in name_classes
        has_firstname = "firstname" in name_classes
        has_patronymic = "patronymic" in name_classes

        if has_surname or has_firstname or has_patronymic:
            score = 0.8
            if sum(1 for c in name_classes if c in ("surname", "firstname", "patronymic")) >= 2:
                score = 0.9
            if len(parts) >= 3:
                score = 0.95

            if not has_firstname and not has_patronymic and _is_suspicious_group(group, text):
                continue

            entities.append(
                {
                    "text": full_text,
                    "label": "PER",
                    "start": start,
                    "end": end,
                    "score": score,
                    "source": "gazetteer",
                }
            )

    return entities


def _is_suspicious_single(word_info: dict, text: str) -> bool:
    after = text[word_info["end"] :].lstrip()
    first_word_after = after.split()[0].lower().rstrip(".,:;") if after else ""
    if first_word_after in _NAME_CONTEXT_STOPS:
        return True
    before = text[: word_info["start"]].rstrip()
    if before:
        last_word_before = before.split()[-1].lower().rstrip(".,") if before else ""
        if last_word_before in _STREET_PREFIXES:
            return True
    return False


def _is_suspicious_group(group: list[dict], text: str) -> bool:
    last = group[-1]
    after = text[last["end"] :].lstrip()
    first_word_after = after.split()[0].lower().rstrip(".,:;") if after else ""
    if first_word_after in _NAME_CONTEXT_STOPS:
        return True
    first = group[0]
    before = text[: first["start"]].rstrip()
    if before:
        last_word_before = before.split()[-1].lower().rstrip(".,") if before else ""
        if last_word_before in _STREET_PREFIXES:
            return True
    return False
