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
if [ -d "$VENV_DIR" ]; then
    info "Virtual environment already exists: $VENV_DIR"
else
    info "Creating virtual environment..."
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        error "Failed to create virtual environment."
        error "On Debian/Ubuntu: sudo apt install python3-venv"
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

# --- 7. PATH check ---
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
    warn "$BIN_DIR is not in your PATH."
    warn "Add this line to ~/.bashrc (or ~/.zshrc):"
    warn "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    warn "Then reload: source ~/.bashrc"
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
