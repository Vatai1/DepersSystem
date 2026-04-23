# DepersSys

Система деперсонализации данных на основе локальной ИИ-модели. Работает полностью оффлайн — данные не покидают ваш компьютер.

## Возможности

- **ML NER** — HuggingFace модель (`Davlan/distilbert-base-multilingual-cased-ner-hrl`) распознаёт имена, адреса, организации на русском и английском
- **Regex-детекция** — телефоны, email, ИНН, СНИЛС, паспорта, банковские карты, даты, IP-адреса
- **4 режима обработки**:
  - **Подмена** — реалистичные фейковые данные (ФИО → другое ФИО с учётом пола и состава)
  - **Замена** — плейсхолдеры (`[EMAIL]`, `[ИНН]`, `[СНИЛС]`)
  - **Маскирование** — символы `X`/`*`
  - **Удаление** — `[REDACTED]`
- **Форматы файлов**: TXT, PDF, DOCX, CSV, XLSX, PNG/JPG (OCR)
- **React UI** с загрузкой файлов и просмотром результатов
- **REST API** для интеграции

## Быстрый старт

### Дев-окружение

```bash
# Полная настройка (Python venv + npm + модель)
./setup.sh

# Запуск бэкенда + фронтенда
./dev.sh
```

Откройте http://localhost:5173

### Docker

```bash
docker compose up --build
```

Откройте http://localhost:8000

### Вручную

```bash
# Бэкенд
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Фронтенд (в другом терминале)
cd frontend && npm run dev
```

## Арххитектура

```
Входной текст / файл
        │
  ┌─────┴─────┐
  │  ML NER   │  ──  PER, LOC, ORG
  └─────┬─────┘
        │
  ┌─────┴─────┐
  │   Regex   │  ──  PHONE, EMAIL, INN, SNILS, PASSPORT, CARD, DATE, IP
  └─────┬─────┘
        │
  ┌─────┴─────┐
  │   Merge   │  ──  regex приоритет, разрешение пересечений
  └─────┬─────┘
        │
  ┌─────┴──────┐
  │ Apply Mode │  ──  fake / replace / mask / redact
  └─────┬──────┘
        │
   Результат
```

## API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/health` | Статус сервера и модели |
| `GET` | `/api/model` | Информация о модели |
| `POST` | `/api/depersonalize/text` | Деперсонализация текста |
| `POST` | `/api/depersonalize/file` | Деперсонализация файла |
| `GET` | `/api/download/{filename}` | Скачать результат |

### Пример запроса

```bash
curl -X POST http://localhost:8000/api/depersonalize/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Иванов Иван Иванович, +79991234567, ivan@mail.ru", "mode": "fake"}'
```

## Конфигурация

Переменные окружения (префикс `DEPERS_`):

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `DEPERS_MODEL_NAME` | `Davlan/distilbert-base-multilingual-cased-ner-hrl` | Модель HuggingFace |
| `DEPERS_DEVICE` | `cpu` | `cpu` или `cuda` |
| `DEPERS_PORT` | `8000` | Порт бэкенда |
| `DEPERS_DATA_DIR` | `data` | Папка для временных файлов |
| `DEPERS_OCR_LANGUAGES` | `["ru","en"]` | Языки для OCR |

## Требования

- Python 3.10–3.13
- Node.js 18+
- ~500 MB для модели (автоматическая загрузка при первом запуске)
- GPU опционально (CUDA) для ускорения

## Лицензия

MIT
