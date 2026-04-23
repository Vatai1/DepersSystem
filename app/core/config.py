from pydantic_settings import BaseSettings

MODEL_REGISTRY = {
    "Davlan/distilbert-base-multilingual-cased-ner-hrl": {
        "display_name": "Multilingual DistilBERT NER",
        "scheme": "standard",
        "description": "Мультиязычная модель. Определяет PER, LOC, ORG.",
        "size": "~0.27B params",
    },
    "Gherman/bert-base-NER-Russian": {
        "display_name": "Russian BERT NER (Detailed)",
        "scheme": "detailed",
        "description": (
            "Русская модель. Определяет FIRST_NAME, LAST_NAME, MIDDLE_NAME, CITY, STREET и др."
        ),
        "size": "~0.2B params",
    },
}


class Settings(BaseSettings):
    model_name: str = "Davlan/distilbert-base-multilingual-cased-ner-hrl"
    device: str = "cpu"
    host: str = "0.0.0.0"
    port: int = 8000
    models_dir: str = "models"
    data_dir: str = "data"
    max_file_size: int = 100 * 1024 * 1024
    ocr_languages: list[str] = ["ru", "en"]

    model_config = {"env_prefix": "DEPERS_"}


settings = Settings()
