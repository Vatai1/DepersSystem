from transformers import pipeline
from app.core import settings, logger


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
        self._device = settings.device

    def load(self):
        if self._pipeline is not None:
            return
        logger.info(f"Loading model {settings.model_name} on {self._device}...")
        try:
            self._pipeline = pipeline(
                "ner",
                model=settings.model_name,
                device=-1 if self._device == "cpu" else 0,
                aggregation_strategy="simple",
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning(
                "Server will start without ML model — only regex-based detection will work"
            )

    @property
    def pipeline(self):
        if self._pipeline is None:
            self.load()
        return self._pipeline

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    _LABEL_WHITELIST = {"PER", "LOC", "ORG"}
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

    def predict(self, text: str) -> list[dict]:
        if self._pipeline is None:
            return []
        results = self.pipeline(text)
        cleaned = []
        for r in results:
            if float(r["score"]) < 0.7 or r["entity_group"] not in self._LABEL_WHITELIST:
                continue
            word = r["word"].strip()
            start = r["start"]
            end = r["end"]
            if r["entity_group"] == "PER":
                lower = word.lower()
                for prefix in self._PER_PREFIXES:
                    if lower.startswith(prefix):
                        offset = len(prefix)
                        word = word[offset:].strip()
                        start += offset
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


model_manager = ModelManager()
