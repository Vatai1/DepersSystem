# AGENTS.md

## Build / Lint / Test

### Backend (Python)

```bash
source .venv/bin/activate

# Lint
ruff check app/

# Type check (if mypy installed)
mypy app/

# Run all tests
pytest

# Run a single test file
pytest tests/test_text_pipeline.py

# Run a single test by name
pytest tests/test_text_pipeline.py::test_depersonalize_fake_mode -v
```

### Frontend (React + TypeScript)

```bash
cd frontend

# Type check
npx tsc --noEmit

# Build
npm run build

# Lint
npm run lint

# Dev server (proxies /api to localhost:8000)
npm run dev
```

### Full dev environment

```bash
./setup.sh          # First-time setup (venv, npm, model download)
./dev.sh            # Start backend + frontend together
```

### Docker

```bash
docker compose up --build
```

## Project Structure

```
app/                          # Python backend
  core/
    config.py                 # Pydantic settings, env vars (DEPERS_* prefix)
    logger.py                 # Loguru logger
    patterns.py               # Regex patterns for PHONE, EMAIL, INN, SNILS, etc.
  services/
    model_manager.py          # Singleton, HuggingFace NER pipeline loader
    text_pipeline.py          # ML NER + regex scan → merge → apply mode
    fake_generator.py         # Realistic FIO-aware fake data generation
    file_pipeline.py          # TXT/PDF/DOCX/CSV/XLSX/image processing
    tabular_pipeline.py       # CSV/Excel column-by-column processing
    image_pipeline.py         # OCR + blur/ blackout regions
  api/
    routes.py                 # FastAPI endpoints (/api/*)
  main.py                     # App factory, lifespan, SPA serving

frontend/                     # React + TypeScript + Vite
  src/
    api/                      # Axios client + TypeScript types
    components/               # Layout, EntityList, FileDropzone
    pages/                    # TextPage, FilePage, HistoryPage
```

## Code Style

### Python

- **Formatter/linter**: Ruff — `line-length = 100`, target `py310`
- **Imports**: stdlib → third-party → local (`from app.core import ...`)
- **No comments** in code unless explicitly requested
- **Types**: use Python 3.10+ syntax (`list[str]`, `dict[str, int]`, `X | None`)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE` for constants
- **Error handling**: catch specific exceptions, use `try/finally` for resource cleanup, log errors with `logger`
- **Pydantic models** for API request/response schemas (`BaseModel`)
- **Settings** via `pydantic_settings.BaseSettings` with `DEPERS_` env prefix
- **Singleton pattern** for `ModelManager` (shared across app lifecycle)

### TypeScript / React

- **Strict mode** enabled (`noUnusedLocals`, `noUnusedParameters`, `verbatimModuleSyntax`)
- **No comments** unless explicitly requested
- **Naming**: `PascalCase` for components/types, `camelCase` for functions/variables
- **Exports**: named exports for components, default export one per page
- **CSS**: co-located `.css` files per component, CSS variables in `index.css`
- **State**: React hooks (`useState`, `useEffect`), no state management library
- **API calls**: centralized in `src/api/client.ts`, types in `src/api/types.ts`

## Architecture

### Depersonalization Pipeline

1. **ML NER** — HuggingFace model detects PER, LOC, ORG entities
2. **Regex scan** — patterns detect PHONE, EMAIL, INN, SNILS, PASSPORT, CARD, DATE, IP
3. **Merge** — regex entities take priority over ML; overlapping spans resolved (longest wins, regex preferred)
4. **Apply mode** — one of four modes:
   - `fake` — realistic substitution (FIO-aware, gender-matched, consistent per-session)
   - `replace` — placeholder tags (`[EMAIL]`, `[ИНН]`, `[PER]`)
   - `mask` — character masking (`X`, `*`)
   - `redact` — full removal (`[REDACTED]`)

### Key Design Decisions

- Regex always wins over ML when spans overlap (prevents ORG false positives on words like "ИНН", "СНИЛС")
- ORG entities from ML are filtered via `_ORG_BLACKLIST` (common non-org words)
- PER prefix stripping removes "Пациент", "Доктор" etc. from detected name spans
- `FakeGenerator` maintains per-session maps so identical names get identical replacements
- FIO splitting classifies each word as surname/firstname/patronymic; only detected parts are replaced

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check + model status |
| GET | `/api/model` | Model info |
| POST | `/api/depersonalize/text` | Depersonalize text body `{text, mode}` |
| POST | `/api/depersonalize/file` | Upload file for processing |
| GET | `/api/download/{filename}` | Download processed file |

## Environment Variables

All prefixed with `DEPERS_`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEPERS_MODEL_NAME` | `Davlan/distilbert-base-multilingual-cased-ner-hrl` | HuggingFace model ID |
| `DEPERS_DEVICE` | `cpu` | `cpu` or `cuda` |
| `DEPERS_PORT` | `8000` | Backend port |
| `DEPERS_DATA_DIR` | `data` | Temp file storage |
| `DEPERS_MODELS_DIR` | `models` | Local model cache |
| `DEPERS_OCR_LANGUAGES` | `["ru","en"]` | EasyOCR languages |
