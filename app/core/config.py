from pydantic_settings import BaseSettings


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
