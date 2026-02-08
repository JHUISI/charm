#!/bin/bash
#
# Charm-Crypto Installation Script
# Supports: Ubuntu/Debian, Fedora/RHEL/CentOS, Arch Linux, and macOS
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/JHUISI/charm/dev/install.sh | bash
#   curl -sSL ... | bash -s -- --from-source
#
# Options:
#   --from-pypi     Install from PyPI (default)
#   --from-source   Clone and build from source
#   --deps-only     Only install system dependencies
#   --no-sudo       Don't use sudo (for containers)
#   --prefix=PATH   Installation prefix (default: /usr/local)
#   --python=PATH   Path to Python interpreter
#   --help          Show this help message

set -euo pipefail

# Configuration
CHARM_VERSION="0.62"
PBC_VERSION="1.0.0"
CHARM_REPO="https://github.com/JHUISI/charm.git"
PBC_URL="https://crypto.stanford.edu/pbc/files/pbc-${PBC_VERSION}.tar.gz"

# Default options
INSTALL_MODE="pypi"
USE_SUDO="yes"
PREFIX="/usr/local"
PYTHON_PATH=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detected values (set by detect_os)
OS=""
ARCH=""
DISTRO=""
HOMEBREW_PREFIX=""
PYTHON=""
SUDO=""

#######################################
# Logging functions
#######################################
info() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
fatal() { error "$*"; exit 1; }

#######################################
# OS Detection
#######################################
detect_os() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"

    case "$OS" in
        Linux)
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO="$ID"
            else
                DISTRO="unknown"
            fi
            ;;
        Darwin)
            DISTRO="macos"
            if [ "$ARCH" = "arm64" ]; then
                HOMEBREW_PREFIX="/opt/homebrew"
            else
                HOMEBREW_PREFIX="/usr/local"
            fi
            ;;
        *)
            fatal "Unsupported operating system: $OS"
            ;;
    esac

    info "Detected: $OS ($DISTRO) on $ARCH"
}

#######################################
# Python Detection
#######################################
detect_python() {
    if [ -n "$PYTHON_PATH" ]; then
        PYTHON="$PYTHON_PATH"
    else
        for py in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
            if command -v "$py" &> /dev/null; then
                local version
                version=$("$py" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
                local major minor
                major=$(echo "$version" | cut -d. -f1)
                minor=$(echo "$version" | cut -d. -f2)
                if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
                    PYTHON="$py"
                    break
                fi
            fi
        done
    fi

    if [ -z "${PYTHON:-}" ]; then
        fatal "Python 3.8+ not found. Please install Python 3.8 or later."
    fi

    info "Using Python: $PYTHON ($($PYTHON --version))"
}

#######################################
# Install System Dependencies
#######################################
install_deps_ubuntu() {
    info "Installing dependencies for Ubuntu/Debian..."
    $SUDO apt-get update
    $SUDO apt-get install -y \
        build-essential gcc g++ make flex bison m4 wget git \
        python3 python3-dev python3-pip python3-venv \
        libgmp-dev libssl-dev
    success "Ubuntu/Debian dependencies installed"
}

install_deps_fedora() {
    info "Installing dependencies for Fedora/RHEL..."
    $SUDO dnf install -y \
        gcc gcc-c++ make flex flex-devel bison m4 wget git \
        python3 python3-devel python3-pip \
        gmp-devel openssl-devel \
        diffutils coreutils
    success "Fedora/RHEL dependencies installed"
}

install_deps_arch() {
    info "Installing dependencies for Arch Linux..."
    $SUDO pacman -S --noconfirm --needed \
        base-devel flex bison wget git m4 \
        python python-pip \
        gmp openssl
    success "Arch Linux dependencies installed"
}

install_deps_macos() {
    info "Installing dependencies for macOS..."

    if ! command -v brew &> /dev/null; then
        warn "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [ "$ARCH" = "arm64" ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi

    brew install gmp openssl@3 wget python@3 || true
    success "macOS dependencies installed"
}

install_system_deps() {
    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            install_deps_ubuntu
            ;;
        fedora)
            install_deps_fedora
            ;;
        rhel|centos|rocky|alma|ol)
            # RHEL-based distros may need EPEL
            if ! $SUDO dnf repolist | grep -q epel; then
                info "Enabling EPEL repository..."
                $SUDO dnf install -y epel-release 2>/dev/null || true
            fi
            install_deps_fedora
            ;;
        arch|manjaro|endeavouros|artix)
            install_deps_arch
            ;;
        macos)
            install_deps_macos
            ;;
        *)
            # Try to detect by package manager
            if command -v apt-get &> /dev/null; then
                warn "Unknown distro '$DISTRO', but apt-get found. Trying Ubuntu/Debian method..."
                install_deps_ubuntu
            elif command -v dnf &> /dev/null; then
                warn "Unknown distro '$DISTRO', but dnf found. Trying Fedora method..."
                install_deps_fedora
            elif command -v pacman &> /dev/null; then
                warn "Unknown distro '$DISTRO', but pacman found. Trying Arch method..."
                install_deps_arch
            elif command -v yum &> /dev/null; then
                warn "Unknown distro '$DISTRO', but yum found. Trying RHEL method..."
                $SUDO yum install -y \
                    gcc gcc-c++ make flex bison m4 wget git \
                    python3 python3-devel python3-pip \
                    gmp-devel openssl-devel
                success "Dependencies installed via yum"
            else
                fatal "Unsupported distribution: $DISTRO. Please install dependencies manually."
            fi
            ;;
    esac
}

#######################################
# Build and Install PBC Library
#######################################
install_pbc() {
    info "Building PBC library v${PBC_VERSION}..."

    # Check if already installed
    if [ -f "${PREFIX}/lib/libpbc.so" ] || [ -f "${PREFIX}/lib/libpbc.dylib" ] || \
       [ -f "${PREFIX}/lib/libpbc.a" ]; then
        success "PBC library already installed at ${PREFIX}/lib"
        return 0
    fi

    local TMPDIR
    TMPDIR=$(mktemp -d)
    cd "$TMPDIR"

    info "Downloading PBC from ${PBC_URL}..."
    wget -q "$PBC_URL" -O "pbc-${PBC_VERSION}.tar.gz"
    tar xzf "pbc-${PBC_VERSION}.tar.gz"
    cd "pbc-${PBC_VERSION}"

    info "Configuring PBC..."

    # PBC's configure script requires yywrap from libfl, but modern flex doesn't always provide it
    # Create a stub library if needed
    if ! echo 'int yywrap(void) { return 1; }' | gcc -c -x c - -o /tmp/yywrap.o 2>/dev/null; then
        warn "Could not create yywrap stub"
    else
        ar rcs /tmp/libfl.a /tmp/yywrap.o 2>/dev/null || true
    fi

    if [ "$DISTRO" = "macos" ]; then
        ./configure --prefix="$PREFIX" \
            LDFLAGS="-L${HOMEBREW_PREFIX}/lib -lgmp" \
            CPPFLAGS="-I${HOMEBREW_PREFIX}/include"
    else
        # Add /tmp to library path for our stub libfl if needed
        ./configure --prefix="$PREFIX" LDFLAGS="-L/tmp -lgmp"
    fi

    info "Building PBC (this may take a few minutes)..."
    local NPROC
    NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    make -j"$NPROC"

    info "Installing PBC..."
    $SUDO make install

    # Update library cache on Linux
    if [ "$OS" = "Linux" ]; then
        $SUDO ldconfig
    fi

    # Cleanup
    cd /
    rm -rf "$TMPDIR"

    success "PBC library installed to ${PREFIX}"
}

#######################################
# Install Charm-Crypto
#######################################
install_from_pypi() {
    info "Installing Charm-Crypto v${CHARM_VERSION} from PyPI..."

    # Set library/include paths
    if [ "$OS" = "Linux" ]; then
        export LD_LIBRARY_PATH="${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
    elif [ "$OS" = "Darwin" ]; then
        export DYLD_LIBRARY_PATH="${PREFIX}/lib:${DYLD_LIBRARY_PATH:-}"
        export LDFLAGS="-L${PREFIX}/lib -L${HOMEBREW_PREFIX}/lib"
        export CFLAGS="-I${PREFIX}/include -I${HOMEBREW_PREFIX}/include"
        export CPPFLAGS="-I${PREFIX}/include -I${HOMEBREW_PREFIX}/include"
    fi

    # Arch Linux and some other distros use PEP 668 which requires --break-system-packages
    local PIP_EXTRA_ARGS=""
    if [ -f /etc/arch-release ] || [ "$DISTRO" = "arch" ] || [ "$DISTRO" = "manjaro" ]; then
        PIP_EXTRA_ARGS="--break-system-packages"
    fi

    $PYTHON -m pip install --upgrade pip $PIP_EXTRA_ARGS
    $PYTHON -m pip install "charm-crypto-framework==${CHARM_VERSION}" $PIP_EXTRA_ARGS

    success "Charm-Crypto installed from PyPI"
}

install_from_source() {
    info "Installing Charm-Crypto from source..."

    local TMPDIR
    TMPDIR=$(mktemp -d)
    cd "$TMPDIR"

    info "Cloning Charm repository..."
    git clone "$CHARM_REPO"
    cd charm

    info "Configuring Charm..."
    if [ "$DISTRO" = "macos" ]; then
        ./configure.sh --enable-darwin --prefix="$PREFIX"
    else
        ./configure.sh --prefix="$PREFIX"
    fi

    info "Building Charm (this may take several minutes)..."
    local NPROC
    NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    make -j"$NPROC"

    info "Installing Charm..."
    $SUDO make install

    if [ "$OS" = "Linux" ]; then
        $SUDO ldconfig
    fi

    # Cleanup
    cd /
    rm -rf "$TMPDIR"

    success "Charm-Crypto installed from source"
}


#######################################
# Verify Installation
#######################################
verify_installation() {
    info "Verifying installation..."

    # Set library paths for verification
    if [ "$OS" = "Linux" ]; then
        export LD_LIBRARY_PATH="${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
    elif [ "$OS" = "Darwin" ]; then
        export DYLD_LIBRARY_PATH="${PREFIX}/lib:${DYLD_LIBRARY_PATH:-}"
    fi

    local TESTS_PASSED=0
    local TESTS_TOTAL=3

    # Test 1: Version check
    if $PYTHON -c "import charm; print(f'Version: {charm.__version__}')" 2>/dev/null; then
        success "Version check passed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "Version check failed (optional - older versions may not have __version__)"
    fi

    # Test 2: Core module import
    if $PYTHON -c "from charm.toolbox.ecgroup import ECGroup; print('ECGroup: OK')" 2>/dev/null; then
        success "ECGroup module works"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        error "ECGroup module failed"
    fi

    # Test 3: Threshold ECDSA (new in v0.62)
    if $PYTHON -c "from charm.schemes.threshold.gg18_dkg import GG18_DKG; print('Threshold ECDSA: OK')" 2>/dev/null; then
        success "Threshold ECDSA schemes available"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "Threshold ECDSA import failed (optional)"
    fi

    echo ""
    if [ "$TESTS_PASSED" -ge 2 ]; then
        success "Verification complete: ${TESTS_PASSED}/${TESTS_TOTAL} tests passed"
        return 0
    else
        error "Verification failed: ${TESTS_PASSED}/${TESTS_TOTAL} tests passed"
        return 1
    fi
}

#######################################
# Configure Shell Environment
#######################################
configure_shell() {
    info "Configuring shell environment..."

    local SHELL_RC=""
    case "${SHELL:-/bin/bash}" in
        */zsh) SHELL_RC="$HOME/.zshrc" ;;
        */bash) SHELL_RC="$HOME/.bashrc" ;;
        *) SHELL_RC="$HOME/.profile" ;;
    esac

    local LIB_VAR=""
    if [ "$OS" = "Linux" ]; then
        LIB_VAR="LD_LIBRARY_PATH"
    elif [ "$OS" = "Darwin" ]; then
        LIB_VAR="DYLD_LIBRARY_PATH"
    fi

    if [ -n "$LIB_VAR" ]; then
        local ENV_LINE="export ${LIB_VAR}=${PREFIX}/lib:\$${LIB_VAR}"

        if ! grep -q "charm-crypto" "$SHELL_RC" 2>/dev/null; then
            {
                echo ""
                echo "# charm-crypto library paths (added by install.sh)"
                echo "$ENV_LINE"
            } >> "$SHELL_RC"
            info "Added library paths to $SHELL_RC"
            warn "Run 'source $SHELL_RC' or restart your shell to apply changes"
        else
            info "Shell already configured for charm-crypto"
        fi
    fi
}

#######################################
# Print Usage
#######################################
usage() {
    cat << EOF
Charm-Crypto Installation Script v${CHARM_VERSION}

Supported Platforms:
  - Ubuntu/Debian (and derivatives: Linux Mint, Pop!_OS)
  - Fedora/RHEL/CentOS (and derivatives: Rocky, Alma, Oracle Linux)
  - Arch Linux (and derivatives: Manjaro, EndeavourOS, Artix)
  - macOS (Intel and Apple Silicon)

Usage: $0 [OPTIONS]

Options:
  --from-pypi     Install from PyPI (default, recommended)
  --from-source   Clone and build from source
  --deps-only     Only install system dependencies and PBC
  --no-sudo       Don't use sudo (for containers/CI)
  --prefix=PATH   Installation prefix (default: /usr/local)
  --python=PATH   Path to Python interpreter
  --help, -h      Show this help message

Examples:
  # Default installation (recommended)
  curl -sSL https://raw.githubusercontent.com/JHUISI/charm/dev/install.sh | bash

  # Install from source
  curl -sSL ... | bash -s -- --from-source

  # Install in container without sudo
  ./install.sh --no-sudo

  # Only install dependencies (for development)
  ./install.sh --deps-only
EOF
}

#######################################
# Main
#######################################
main() {
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --from-pypi) INSTALL_MODE="pypi" ;;
            --from-source) INSTALL_MODE="source" ;;
            --deps-only) INSTALL_MODE="deps-only" ;;
            --no-sudo) USE_SUDO="no" ;;
            --prefix=*) PREFIX="${1#*=}" ;;
            --python=*) PYTHON_PATH="${1#*=}" ;;
            --help|-h) usage; exit 0 ;;
            *) warn "Unknown option: $1" ;;
        esac
        shift
    done

    # Banner
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║         Charm-Crypto Installation Script                  ║"
    echo "║                   Version ${CHARM_VERSION}                          ║"
    echo "║  (Ubuntu/Debian, Fedora/RHEL, Arch Linux, macOS)         ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    # Set up sudo
    if [ "$USE_SUDO" = "yes" ] && [ "$(id -u)" -ne 0 ]; then
        SUDO="sudo"
        info "Will use sudo for system installations"
    else
        SUDO=""
        if [ "$(id -u)" -eq 0 ]; then
            info "Running as root"
        else
            info "Running without sudo (--no-sudo)"
        fi
    fi

    # Run installation steps
    detect_os
    install_system_deps
    detect_python  # Detect Python AFTER installing deps (which may install Python)
    install_pbc

    if [ "$INSTALL_MODE" != "deps-only" ]; then
        if [ "$INSTALL_MODE" = "pypi" ]; then
            install_from_pypi
        else
            install_from_source
        fi

        verify_installation
        configure_shell

        echo ""
        success "═══════════════════════════════════════════════════════════"
        success "  Installation complete!"
        success "═══════════════════════════════════════════════════════════"
        echo ""
        echo "Next steps:"
        echo "  1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
        echo "  2. Test the installation:"
        echo "     python3 -c \"from charm.toolbox.pairinggroup import PairingGroup; print('OK')\""
        echo ""
    else
        echo ""
        success "Dependencies installed. You can now build Charm from source:"
        echo "  git clone ${CHARM_REPO}"
        echo "  cd charm"
        echo "  ./configure.sh && make && sudo make install"
        echo ""
    fi
}

main "$@"

