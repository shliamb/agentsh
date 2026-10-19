#!/bin/bash
#
# Agent Shell — installer.
# Creates a virtual environment, installs dependencies,
# and registers the `agentsh` command in ~/.local/bin.
#
set -e

# --- colors ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { printf "${GREEN}[install]${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}[warn]${NC} %s\n" "$1"; }
error() { printf "${RED}[error]${NC} %s\n" "$1" >&2; }

# --- paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"
ENTRYPOINT="$SCRIPT_DIR/agentshell/main.py"
BIN_DIR="$HOME/.local/bin"

echo
info "Agent Shell — installer"
info "Source: $SCRIPT_DIR"
echo

# --- 1. python3 present ---
if ! command -v python3 >/dev/null 2>&1; then
    error "python3 not found in PATH. Install Python 3.10+ first."
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    error "Python 3.10+ required, found $PY_VER"
    exit 1
fi
info "Python $PY_VER ✓"

# --- 2. entrypoint present ---
if [ ! -f "$ENTRYPOINT" ]; then
    error "Entrypoint not found: $ENTRYPOINT"
    error "Is this the root of the agentsh repository?"
    exit 1
fi

# --- 3. create venv ---
# Проверяем не просто папку, а что внутри есть рабочий питон
if [ -f "$VENV_DIR/bin/python" ]; then
    info "Virtual environment already exists: $VENV_DIR"
else
    # Если папка есть, но она битая (без python) — удаляем её
    if [ -d "$VENV_DIR" ]; then
        warn "Found broken virtual environment. Recreating..."
        rm -rf "$VENV_DIR"
    fi
    
    info "Creating virtual environment..."
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        # Если упало — подчищаем за собой мусор
        rm -rf "$VENV_DIR"
        error "Failed to create virtual environment."
        error "Missing 'python3-venv' package."
        error "On Debian/Ubuntu run: sudo apt install python3-venv"
        error "On Fedora run: sudo dnf install python3-devel"
        exit 1
    fi
    info "Virtual environment created ✓"
fi

# --- 4. upgrade pip ---
info "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
info "pip upgraded ✓"

# --- 5. install requirements ---
if [ -f "$REQUIREMENTS" ]; then
    info "Installing dependencies from requirements.txt..."
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS" --quiet
    info "Dependencies installed ✓"
else
    warn "requirements.txt not found — skipping dependency install"
fi

# --- 6. create wrappers ---
mkdir -p "$BIN_DIR"
for name in agentsh agentshell; do
    WRAPPER="$BIN_DIR/$name"
    cat > "$WRAPPER" <<EOF
#!/bin/bash
exec "$VENV_DIR/bin/python" "$ENTRYPOINT" "\$@"
EOF
    chmod +x "$WRAPPER"
    info "Wrapper created: $WRAPPER ✓"
done

# --- 7. PATH check & auto-add ---
# Проверяем, есть ли уже ~/.local/bin в PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not in your PATH."
    
    # Определяем файл конфигурации шелла
    SHELL_RC=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi

    # Проверяем, нет ли уже этой строки в файле (чтобы не дублировать при повторной установке)
    if [ -n "$SHELL_RC" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC" 2>/dev/null; then
        info "Adding ~/.local/bin to PATH in $SHELL_RC..."
        echo "" >> "$SHELL_RC"
        echo "# Added by Agent Shell installer" >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        info "PATH updated ✓"
    fi

    # Обновляем PATH только для текущего сеанса установки, 
    # чтобы ключи настроились без перезапуска терминала
    export PATH="$BIN_DIR:$PATH"
    
    warn "IMPORTANT: To use 'agentsh' in other terminal windows,"
    warn "please restart your terminal or run: source $SHELL_RC"
fi

# --- 8. done ---
echo
info "Installation complete."
echo
info "Next steps:"
info "    cd /path/to/your/project"
info "    agentsh init"
info "    agentsh"
echo


# --- 9. API keys ---
echo
info "Configuring API keys..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/agentshell/scripts/setup_keys.py" || warn "Key setup skipped. Run 'agentsh setup-keys' later."
