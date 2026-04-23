from transformers import pipeline

from app.core import logger
from app.core.config import MODEL_REGISTRY, settings

_DETAILED_PER_LABELS = {"LAST_NAME", "FIRST_NAME", "MIDDLE_NAME"}
_DETAILED_LOC_LABELS = {"CITY", "COUNTRY", "REGION", "DISTRICT", "STREET", "HOUSE"}
_DETAILED_IGNORE = {"HOUSE"}
_DETAILED_LABEL_MAP = {
    "LAST_NAME": "PER",
    "FIRST_NAME": "PER",
    "MIDDLE_NAME": "PER",
    "CITY": "LOC",
    "COUNTRY": "LOC",
    "REGION": "LOC",
    "DISTRICT": "LOC",
    "STREET": "LOC",
}


class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._pipeline = None
        self._model_name: str = settings.model_name
        self._scheme: str = MODEL_REGISTRY.get(self._model_name, {}).get("scheme", "standard")
        self._device = settings.device

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    def load(self, model_name: str | None = None):
        target = model_name or self._model_name
        if self._pipeline is not None and target == self._model_name:
            return
        if target != self._model_name:
            self._model_name = target
            self._scheme = MODEL_REGISTRY.get(target, {}).get("scheme", "standard")
            self._pipeline = None
        logger.info(f"Loading model {self._model_name} on {self._device}...")
        try:
            self._pipeline = pipeline(
                "ner",
                model=self._model_name,
                device=-1 if self._device == "cpu" else 0,
                aggregation_strategy="simple",
            )
            logger.info(f"Model {self._model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning(
                "Server will start without ML model — only regex-based detection will work"
            )

    def _get_pipeline(self):
        if self._pipeline is None:
            self.load()
        return self._pipeline

    _STANDARD_WHITELIST = {"PER", "LOC", "ORG"}
    _ORG_BLACKLIST = {
        "инн",
        "снилс",
        "паспорт",
        "огрн",
        "огрнип",
        "кпп",
        "бик",
        "корр",
        "расч",
        "лиц",
        "тел",
        "факс",
        "email",
        "e-mail",
        "адрес",
        "расс",
        "прожив",
        "род",
        "пол",
        "inn",
        "snils",
        "passport",
    }
    _PER_PREFIXES = (
        "пациент ",
        "пациентка ",
        "гражданин ",
        "гражданка ",
        "г-н ",
        "г-жа ",
        "товарищ ",
        "полицейский ",
        "доктор ",
        "врач ",
        "профессор ",
        "mr ",
        "mrs ",
        "ms ",
        "dr ",
        "patient ",
    )
    _PER_PREFIX_STEMS = {p.rstrip() for p in _PER_PREFIXES}

    def _predict_standard(self, text: str) -> list[dict]:
        results = self._get_pipeline()(text)
        cleaned = []
        for r in results:
            if float(r["score"]) < 0.7 or r["entity_group"] not in self._STANDARD_WHITELIST:
                continue
            word = r["word"].strip()
            if not word or word.startswith("##"):
                continue
            start = r["start"]
            end = r["end"]
            if r["entity_group"] == "PER":
                lower = word.lower()
                if lower in self._PER_PREFIX_STEMS:
                    continue
                for prefix in self._PER_PREFIXES:
                    if lower.startswith(prefix):
                        prefix_len = len(prefix)
                        after_prefix = word[prefix_len:]
                        rest = after_prefix.strip()
                        if rest:
                            leading_ws = len(after_prefix) - len(after_prefix.lstrip())
                            offset = prefix_len + leading_ws
                            start += offset
                            end = start + len(rest)
                            word = rest
                        break
                if not word:
                    continue
            if r["entity_group"] == "ORG":
                lower = word.lower().rstrip(".,:;")
                if lower in self._ORG_BLACKLIST or any(
                    lower.startswith(b) for b in self._ORG_BLACKLIST
                ):
                    continue
            cleaned.append(
                {
                    "text": word,
                    "label": r["entity_group"],
                    "start": start,
                    "end": end,
                    "score": round(float(r["score"]), 4),
                }
            )
        return cleaned

    def _predict_detailed(self, text: str) -> list[dict]:
        results = self._get_pipeline()(text)
        cleaned = []
        for r in results:
            eg = r["entity_group"]
            if float(r["score"]) < 0.7:
                continue
            word = r["word"].strip()
            if not word or word.startswith("##"):
                continue
            if eg in _DETAILED_IGNORE:
                continue
            if eg in _DETAILED_PER_LABELS:
                cleaned.append(
                    {
                        "text": r["word"].strip(),
                        "label": "PER",
                        "start": r["start"],
                        "end": r["end"],
                        "score": round(float(r["score"]), 4),
                        "sub_label": eg,
                    }
                )
            elif eg in _DETAILED_LOC_LABELS:
                mapped = _DETAILED_LABEL_MAP.get(eg, "LOC")
                cleaned.append(
                    {
                        "text": r["word"].strip(),
                        "label": mapped,
                        "start": r["start"],
                        "end": r["end"],
                        "score": round(float(r["score"]), 4),
                        "sub_label": eg,
                    }
                )
        return cleaned

    def predict(self, text: str) -> list[dict]:
        if self._pipeline is None:
            self.load()
        if self._pipeline is None:
            return []
        if self._scheme == "detailed":
            raw = self._predict_detailed(text)
            return self._group_per_parts(raw)
        return self._predict_standard(text)

    def _group_per_parts(self, entities: list[dict]) -> list[dict]:
        if not entities:
            return entities
        result = []
        i = 0
        while i < len(entities):
            e = entities[i]
            if e["label"] != "PER" or "sub_label" not in e:
                result.append(e)
                i += 1
                continue
            parts = [e]
            j = i + 1
            while j < len(entities):
                nxt = entities[j]
                if nxt["label"] != "PER" or "sub_label" not in nxt:
                    break
                if nxt["start"] - parts[-1]["end"] > 2:
                    break
                parts.append(nxt)
                j += 1
            if len(parts) == 1:
                e_copy = dict(e)
                e_copy.pop("sub_label", None)
                result.append(e_copy)
            else:
                full_text = " ".join(p["text"] for p in parts)
                result.append(
                    {
                        "text": full_text,
                        "label": "PER",
                        "start": parts[0]["start"],
                        "end": parts[-1]["end"],
                        "score": max(p["score"] for p in parts),
                        "per_parts": [
                            {"text": p["text"], "role": p.get("sub_label", "unknown")}
                            for p in parts
                        ],
                    }
                )
            i = j
        return result

    def get_info(self) -> dict:
        info = {
            "model_name": self._model_name,
            "scheme": self._scheme,
            "is_loaded": self.is_loaded,
        }
        reg = MODEL_REGISTRY.get(self._model_name, {})
        if reg:
            info["display_name"] = reg.get("display_name", self._model_name)
            info["description"] = reg.get("description", "")
            info["size"] = reg.get("size", "")
        return info


model_manager = ModelManager()
