#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "  ${CYAN}▸${NC} $*"; }
ok()    { echo -e "  ${GREEN}✓${NC} $*"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $*"; }
err()   { echo -e "  ${RED}✗${NC} $*" >&2; }

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PROGRESS_PID=""

TOTAL_STEPS=7
CURRENT_STEP=0

step_header() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo ""
    echo -e "  ${BOLD}${DIM}[$CURRENT_STEP/$TOTAL_STEPS]${NC} ${BOLD}$*${NC}"
    echo -e "  ${DIM}──────────────────────────────────${NC}"
}

progress_bar() {
    local duration=${1:-60}
    local label=${2:-Working}
    local width=30
    local fill_char="█"
    local empty_char="░"

    (
        local elapsed=0
        while [ $elapsed -lt $duration ]; do
            local pct=$(( (elapsed * 100) / duration ))
            local filled=$(( (elapsed * width) / duration ))
            local empty=$(( width - filled ))
            local bar=""
            for ((i=0; i<filled; i++)); do bar+="${fill_char}"; done
            for ((i=0; i<empty; i++)); do bar+="${empty_char}"; done
            printf "\r  ${CYAN}%s${NC} ${DIM}%s${NC} ${BOLD}%3d%%${NC}" "$label" "$bar" "$pct"
            sleep 1
            elapsed=$((elapsed + 1))
        done
        printf "\r  ${GREEN}%s${NC} ${DIM}%s${NC} ${BOLD}100%%${NC}" "$label" "$(printf '%*s' "$width" '' | tr ' ' "$fill_char")"
        echo ""
    ) &
    PROGRESS_PID=$!
}

stop_progress() {
    if [ -n "$PROGRESS_PID" ] && kill -0 "$PROGRESS_PID" 2>/dev/null; then
        kill "$PROGRESS_PID" 2>/dev/null || true
        wait "$PROGRESS_PID" 2>/dev/null || true
        PROGRESS_PID=""
    fi
    printf "\r%*s\r" 80 ""
}

check_cmd() {
    command -v "$1" &>/dev/null
}

find_python() {
    local candidates=("python3.12" "python3.13" "python3.11" "python3.10")
    for py in "${candidates[@]}"; do
        if check_cmd "$py"; then
            echo "$py"
            return 0
        fi
    done
    if check_cmd python3 && python3 -c "import sys; exit(0 if sys.version_info < (3, 14) and sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
        echo "python3"
        return 0
    fi
    return 1
}

step_python() {
    step_header "Python-окружение"

    info "Поиск подходящего Python (3.10–3.13)..."
    local PYTHON
    if ! PYTHON=$(find_python); then
        err "Подходящий Python не найден. Установите: brew install python@3.12"
        exit 1
    fi
    local py_version
    py_version=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    ok "$PYTHON ($py_version)"

    if [ -d "$VENV_DIR" ]; then
        ok "venv уже существует"
    else
        info "Создание venv..."
        $PYTHON -m venv "$VENV_DIR"
        ok "venv создан"
    fi

    source "$VENV_DIR/bin/activate"

    info "Обновление pip, setuptools, wheel..."
    pip install --progress-bar on --upgrade pip setuptools wheel 2>&1 | (
        while IFS= read -r line; do
            if [[ "$line" =~ [0-9]+% ]]; then
                local pct=$(echo "$line" | grep -oE '[0-9]+%' | head -1 | tr -d '%')
                local filled=$(( pct / 3 ))
                local bar=""
                for ((i=0; i<filled; i++)); do bar+="█"; done
                for ((i=filled; i<33; i++)); do bar+="░"; done
                printf "\r  ${CYAN}pip${NC} %s ${BOLD}%3s%%${NC}" "$bar" "$pct"
            fi
        done
    )
    echo ""
    ok "pip обновлён"

    info "Установка Python-зависимостей (это может занять несколько минут)..."
    pip install --progress-bar on -e "$PROJECT_ROOT[dev]" 2>&1 | (
        local pkgs=0
        local collecting=0
        while IFS= read -r line; do
            if [[ "$line" == "Collecting"* ]]; then
                collecting=$((collecting + 1))
                printf "\r  ${DIM}Сборка пакетов... %d${NC}" "$collecting"
            elif [[ "$line" == "Downloading"* ]]; then
                local pct=$(echo "$line" | grep -oE '[0-9]+%' | head -1 | tr -d '%')
                local name=$(echo "$line" | grep -oE '[a-zA-Z0-9_-]+' | head -1)
                if [ -n "$pct" ]; then
                    local filled=$(( pct / 4 ))
                    local bar=""
                    for ((i=0; i<filled; i++)); do bar+="█"; done
                    for ((i=filled; i<25; i++)); do bar+="░"; done
                    printf "\r  ${CYAN}↓${NC} %-25s %s ${BOLD}%3s%%${NC}" "$name" "$bar" "$pct"
                fi
            elif [[ "$line" == "Installing"* ]] || [[ "$line" == "Building"* ]]; then
                pkgs=$((pkgs + 1))
                printf "\r  ${DIM}Установка... пакет #%d${NC}           " "$pkgs"
            elif [[ "$line" == "Successfully"* ]]; then
                printf "\r  ${GREEN}✓${NC} Все пакеты установлены              "
                echo ""
            fi
        done
    )
    ok "Python-зависимости установлены"

    info "Проверка CUDA..."
    if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        local gpu_name
        gpu_name=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))")
        ok "GPU: $gpu_name"
    else
        warn "GPU не обнаружен, будет использоваться CPU"
    fi
}

step_node() {
    step_header "Frontend-зависимости"

    if ! check_cmd node; then
        err "Node.js не найден. Установите: brew install node"
        exit 1
    fi
    ok "Node $(node -v), npm $(npm -v)"

    info "Установка npm-пакетов..."
    cd "$FRONTEND_DIR"

    npm install --legacy-peer-deps 2>&1 | (
        local total=""
        local current=0
        while IFS= read -r line; do
            if [[ "$line" == *"packages in"* ]]; then
                printf "\r  ${GREEN}✓${NC} %s              " "$line"
                echo ""
            elif [[ "$line" == *"fetch"* ]] || [[ "$line" == *"http"* ]]; then
                current=$((current + 1))
                printf "\r  ${DIM}Скачивание пакетов... #%d${NC}          " "$current"
            elif [[ "$line" == *"reify"* ]] || [[ "$line" == *"link"* ]]; then
                current=$((current + 1))
                printf "\r  ${DIM}Установка... #%d${NC}                    " "$current"
            fi
        done
    )
    ok "Frontend-зависимости установлены"
    cd "$PROJECT_ROOT"
}

step_build_frontend() {
    step_header "Сборка frontend"

    info "TypeScript + Vite build..."
    cd "$FRONTEND_DIR"
    npm run build 2>&1 | (
        while IFS= read -r line; do
            if [[ "$line" == *"transforming"* ]]; then
                printf "\r  ${DIM}Трансформация модулей...${NC}        "
            elif [[ "$line" == *"rendering"* ]]; then
                printf "\r  ${CYAN}Сборка чанков...${NC}                  "
            elif [[ "$line" == *"✓"*"built"* ]]; then
                printf "\r  ${GREEN}✓${NC} Build завершён                  "
                echo ""
            fi
        done
    )
    ok "frontend/dist/ готов"
    cd "$PROJECT_ROOT"
}

step_dirs() {
    step_header "Рабочие директории"
    mkdir -p "$PROJECT_ROOT/models"
    mkdir -p "$PROJECT_ROOT/data"
    ok "models/ data/"
}

step_env() {
    step_header "Конфигурация"
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        cat > "$PROJECT_ROOT/.env" << 'EOF'
DEPERS_MODEL_NAME=Davlan/distilbert-base-multilingual-cased-ner-hrl
DEPERS_DEVICE=cpu
DEPERS_HOST=0.0.0.0
DEPERS_PORT=8000
DEPERS_MODELS_DIR=models
DEPERS_DATA_DIR=data
DEPERS_OCR_LANGUAGES=["ru","en"]
EOF
        ok ".env создан"
    else
        ok ".env уже существует"
    fi
}

step_model() {
    step_header "ML-модель"

    local model_name
    model_name=$(python3 -c 'from app.core.config import Settings; print(Settings().model_name)' 2>/dev/null || echo "Davlan/distilbert-base-multilingual-cased-ner-hrl")
    local model_slug
    model_slug=$(echo "$model_name" | tr '/' '--')

    info "Модель: $model_name"

    local hf_cache="${HF_HOME:-$HOME/.cache/huggingface}"
    if [ -d "$hf_cache/hub/models--$model_slug" ]; then
        ok "Модель уже в кэше"
        return
    fi

    echo ""
    echo -e "  ${YELLOW}Модель не найдена в кэше.${NC}"
    read -rp "$(echo -e "  ${CYAN}Скачать сейчас? [Y/n]:${NC} ")" answer
    answer="${answer:-Y}"
    if [[ ! "$answer" =~ ^[YyДд]$ ]]; then
        warn "Пропуск. Модель скачается автоматически при первом запуске."
        return
    fi

    info "Загрузка модели из HuggingFace Hub..."
    python3 -c "
import sys, time
from transformers import AutoTokenizer, AutoModelForTokenClassification

model_name = '$model_name'

def download_with_progress():
    print('  ↓ Загрузка токенизатора...', flush=True)
    AutoTokenizer.from_pretrained(model_name)
    print('  ✓ Токенизатор загружен', flush=True)
    print('  ↓ Загрузка модели...', flush=True)
    AutoModelForTokenClassification.from_pretrained(model_name)
    print('  ✓ Модель загружена', flush=True)

download_with_progress()
" 2>&1 | while IFS= read -r line; do
        echo "$line"
    done

    ok "Модель готова"
}

step_check() {
    step_header "Финальная проверка"
    local errors=0

    if "$VENV_DIR/bin/python" -c "import fastapi" 2>/dev/null; then
        ok "fastapi"
    else
        err "fastapi не установлен"
        errors=$((errors + 1))
    fi

    if "$VENV_DIR/bin/python" -c "import transformers" 2>/dev/null; then
        ok "transformers"
    else
        err "transformers не установлен"
        errors=$((errors + 1))
    fi

    if "$VENV_DIR/bin/python" -c "import torch" 2>/dev/null; then
        ok "torch"
    else
        err "torch не установлен"
        errors=$((errors + 1))
    fi

    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        ok "node_modules"
    else
        err "node_modules не найден"
        errors=$((errors + 1))
    fi

    if [ -d "$FRONTEND_DIR/dist" ]; then
        ok "frontend/dist"
    else
        err "frontend/dist не собран"
        errors=$((errors + 1))
    fi

    if [ $errors -eq 0 ]; then
        echo ""
        ok "${BOLD}Все проверки пройдены${NC}"
    else
        echo ""
        err "$errors ошибок"
        return 1
    fi
}

print_banner_done() {
    echo ""
    echo -e "  ${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "  ${GREEN}║${NC}  ${BOLD}Dev-окружение готово!${NC}                     ${GREEN}║${NC}"
    echo -e "  ${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${CYAN}Запуск:${NC}"
    echo -e "    ${DIM}\$${NC} ./dev.sh"
    echo ""
    echo -e "  ${CYAN}Или вручную:${NC}"
    echo -e "    ${DIM}\$${NC} source .venv/bin/activate"
    echo -e "    ${DIM}\$${NC} uvicorn app.main:app --reload --port 8000"
    echo -e "    ${DIM}\$${NC} cd frontend && npm run dev"
    echo ""
    echo -e "  ${CYAN}Docker:${NC}"
    echo -e "    ${DIM}\$${NC} docker compose up --build"
    echo ""
}

main() {
    echo ""
    echo -e "  ${BOLD}${CYAN}╔═══════════════════════════════════════╗${NC}"
    echo -e "  ${BOLD}${CYAN}║${NC}  ${BOLD}DepersSys — Setup Dev Environment${NC}   ${BOLD}${CYAN}║${NC}"
    echo -e "  ${BOLD}${CYAN}╚═══════════════════════════════════════╝${NC}"

    step_python
    step_node
    step_build_frontend
    step_dirs
    step_env
    step_model
    step_check
    print_banner_done
}

main "$@"
