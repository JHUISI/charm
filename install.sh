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

# Track temp directories for cleanup on error
CLEANUP_DIRS=""

# Cleanup function for error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Installation failed with exit code $exit_code" >&2
    fi
    # Clean up any temp directories we created
    if [ -n "$CLEANUP_DIRS" ]; then
        for dir in $CLEANUP_DIRS; do
            if [ -d "$dir" ]; then
                rm -rf "$dir" 2>/dev/null || true
            fi
        done
    fi
}
trap cleanup EXIT

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
                # Use format() instead of f-strings for Python 2.x compatibility during detection
                version=$("$py" -c "import sys; print('{0}.{1}'.format(sys.version_info.major, sys.version_info.minor))" 2>/dev/null)
                if [ -z "$version" ]; then
                    continue
                fi
                local major minor
                major=$(echo "$version" | cut -d. -f1)
                minor=$(echo "$version" | cut -d. -f2)
                # Check for Python 3.8+ (major > 3, or major == 3 and minor >= 8)
                if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; }; then
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
        libgmp-dev libssl-dev libntl-dev
    success "Ubuntu/Debian dependencies installed"
}

install_deps_fedora() {
    info "Installing dependencies for Fedora/RHEL..."
    $SUDO dnf install -y \
        gcc gcc-c++ make flex flex-devel bison m4 wget git \
        python3 python3-devel python3-pip \
        gmp-devel openssl-devel ntl-devel \
        diffutils coreutils
    success "Fedora/RHEL dependencies installed"
}

install_deps_arch() {
    info "Installing dependencies for Arch Linux..."
    $SUDO pacman -S --noconfirm --needed \
        base-devel flex bison wget git m4 \
        python python-pip \
        gmp openssl ntl
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

    # Issue #4: Install each package separately with proper error handling
    # Only ignore "already installed" warnings, not genuine failures
    local brew_packages="gmp openssl@3 ntl wget python@3"
    for pkg in $brew_packages; do
        if brew list "$pkg" &>/dev/null; then
            info "$pkg is already installed"
        else
            info "Installing $pkg..."
            if ! brew install "$pkg"; then
                error "Failed to install $pkg"
                fatal "Homebrew package installation failed. Please check the error above."
            fi
        fi
    done
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
            # Issue #5: RHEL-based distros may need EPEL - improved detection for RHEL 9+
            if ! $SUDO dnf repolist 2>/dev/null | grep -qi epel; then
                info "Enabling EPEL repository..."
                # Try epel-release first (works on CentOS, Rocky, Alma)
                if $SUDO dnf install -y epel-release 2>/dev/null; then
                    success "EPEL repository enabled via epel-release"
                # For RHEL proper, try the EPEL RPM directly
                elif command -v subscription-manager &> /dev/null; then
                    # Get RHEL major version
                    local rhel_version
                    rhel_version=$(rpm -E %rhel 2>/dev/null || echo "9")
                    info "Attempting to install EPEL for RHEL ${rhel_version}..."
                    $SUDO dnf install -y "https://dl.fedoraproject.org/pub/epel/epel-release-latest-${rhel_version}.noarch.rpm" 2>/dev/null || \
                        warn "Could not install EPEL - some packages may not be available"
                else
                    warn "Could not enable EPEL repository - some packages may not be available"
                fi
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
                    gmp-devel openssl-devel ntl-devel
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

    local PBC_TMPDIR
    PBC_TMPDIR=$(mktemp -d)
    CLEANUP_DIRS="$CLEANUP_DIRS $PBC_TMPDIR"
    cd "$PBC_TMPDIR"

    info "Downloading PBC from ${PBC_URL}..."
    # Issue #10: Use curl as fallback if wget is not available
    if command -v wget &> /dev/null; then
        wget -q "$PBC_URL" -O "pbc-${PBC_VERSION}.tar.gz"
    elif command -v curl &> /dev/null; then
        curl -sSL "$PBC_URL" -o "pbc-${PBC_VERSION}.tar.gz"
    else
        fatal "Neither wget nor curl found. Please install one of them."
    fi
    tar xzf "pbc-${PBC_VERSION}.tar.gz"
    cd "pbc-${PBC_VERSION}"

    info "Configuring PBC..."

    # Issue #2 & #3: PBC's configure script requires yywrap from libfl, but modern flex doesn't always provide it
    # Create a stub library in our temp directory (not hardcoded /tmp)
    local STUB_DIR="${PBC_TMPDIR}/stubs"
    mkdir -p "$STUB_DIR"
    local STUB_LDFLAGS=""

    if echo 'int yywrap(void) { return 1; }' | gcc -c -x c - -o "${STUB_DIR}/yywrap.o" 2>/dev/null; then
        if ar rcs "${STUB_DIR}/libfl.a" "${STUB_DIR}/yywrap.o" 2>/dev/null; then
            STUB_LDFLAGS="-L${STUB_DIR}"
            info "Created yywrap stub library at ${STUB_DIR}/libfl.a"
        else
            warn "Could not create libfl.a archive - PBC build may fail if flex doesn't provide yywrap"
        fi
    else
        warn "Could not compile yywrap stub - PBC build may fail if flex doesn't provide yywrap"
    fi

    # Add -lfl to link our stub library if we created it
    local FL_LINK=""
    if [ -n "$STUB_LDFLAGS" ]; then
        FL_LINK="-lfl"
    fi

    if [ "$DISTRO" = "macos" ]; then
        ./configure --prefix="$PREFIX" \
            LDFLAGS="-L${HOMEBREW_PREFIX}/lib ${STUB_LDFLAGS} ${FL_LINK} -lgmp" \
            CPPFLAGS="-I${HOMEBREW_PREFIX}/include"
    else
        ./configure --prefix="$PREFIX" LDFLAGS="${STUB_LDFLAGS} ${FL_LINK} -lgmp"
    fi

    info "Building PBC (this may take a few minutes)..."
    local NPROC
    NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    make -j"$NPROC"

    info "Installing PBC..."
    $SUDO make install

    # Issue #7: Update library cache on Linux - use full path or check existence
    if [ "$OS" = "Linux" ]; then
        if command -v ldconfig &> /dev/null; then
            $SUDO ldconfig
        elif [ -x /sbin/ldconfig ]; then
            $SUDO /sbin/ldconfig
        else
            warn "ldconfig not found - you may need to run 'sudo ldconfig' manually"
        fi
    fi

    # Cleanup
    cd /
    rm -rf "$PBC_TMPDIR"

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

    # Issue #6: Detect PEP 668 (externally managed Python) by checking for EXTERNALLY-MANAGED marker
    # This works on Ubuntu 23.04+, Fedora 38+, Debian 12+, Arch, and other modern distros
    local PIP_EXTRA_ARGS=""
    local python_lib_path
    python_lib_path=$($PYTHON -c "import sys; print('{0}/lib/python{1}.{2}'.format(sys.prefix, sys.version_info.major, sys.version_info.minor))" 2>/dev/null)

    # Check for EXTERNALLY-MANAGED marker in Python's lib path or common system locations
    local pep668_detected="no"
    if [ -n "$python_lib_path" ] && [ -f "${python_lib_path}/EXTERNALLY-MANAGED" ]; then
        pep668_detected="yes"
    elif [ -f /usr/lib/python3/EXTERNALLY-MANAGED ]; then
        pep668_detected="yes"
    elif find /usr/lib -maxdepth 2 -name "EXTERNALLY-MANAGED" -print -quit 2>/dev/null | grep -q .; then
        pep668_detected="yes"
    fi

    if [ "$pep668_detected" = "yes" ]; then
        info "Detected PEP 668 externally managed Python environment"
        PIP_EXTRA_ARGS="--break-system-packages"
    fi

    # shellcheck disable=SC2086
    $PYTHON -m pip install --upgrade pip $PIP_EXTRA_ARGS
    # shellcheck disable=SC2086
    $PYTHON -m pip install "charm-crypto-framework==${CHARM_VERSION}" $PIP_EXTRA_ARGS

    success "Charm-Crypto installed from PyPI"
}

install_from_source() {
    info "Installing Charm-Crypto from source..."

    local SOURCE_TMPDIR
    SOURCE_TMPDIR=$(mktemp -d)
    CLEANUP_DIRS="$CLEANUP_DIRS $SOURCE_TMPDIR"
    cd "$SOURCE_TMPDIR"

    # Issue #11: Use --depth 1 for faster clone (only need latest commit)
    info "Cloning Charm repository (shallow clone)..."
    git clone --depth 1 "$CHARM_REPO"
    cd charm

    info "Configuring Charm..."
    if [ "$DISTRO" = "macos" ]; then
        ./configure.sh --enable-darwin --enable-lattice --prefix="$PREFIX"
    else
        ./configure.sh --enable-lattice --prefix="$PREFIX"
    fi

    info "Building Charm (this may take several minutes)..."
    local NPROC
    NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    make -j"$NPROC"

    info "Installing Charm..."
    $SUDO make install

    # Issue #7: Use full path or check existence for ldconfig
    if [ "$OS" = "Linux" ]; then
        if command -v ldconfig &> /dev/null; then
            $SUDO ldconfig
        elif [ -x /sbin/ldconfig ]; then
            $SUDO /sbin/ldconfig
        else
            warn "ldconfig not found - you may need to run 'sudo ldconfig' manually"
        fi
    fi

    # Cleanup
    cd /
    rm -rf "$SOURCE_TMPDIR"

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

    # Test 1: Version check (Issue #8: use format() instead of f-string for consistency)
    if $PYTHON -c "import charm; print('Version: {0}'.format(charm.__version__))" 2>/dev/null; then
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

    # Issue #9: Add fish shell support
    local SHELL_RC=""
    local IS_FISH="no"
    case "${SHELL:-/bin/bash}" in
        */zsh) SHELL_RC="$HOME/.zshrc" ;;
        */bash) SHELL_RC="$HOME/.bashrc" ;;
        */fish)
            SHELL_RC="$HOME/.config/fish/config.fish"
            IS_FISH="yes"
            # Ensure fish config directory exists
            mkdir -p "$HOME/.config/fish"
            ;;
        *) SHELL_RC="$HOME/.profile" ;;
    esac

    local LIB_VAR=""
    if [ "$OS" = "Linux" ]; then
        LIB_VAR="LD_LIBRARY_PATH"
    elif [ "$OS" = "Darwin" ]; then
        LIB_VAR="DYLD_LIBRARY_PATH"
    fi

    if [ -n "$LIB_VAR" ]; then
        if ! grep -q "charm-crypto" "$SHELL_RC" 2>/dev/null; then
            if [ "$IS_FISH" = "yes" ]; then
                # Fish shell uses different syntax
                {
                    echo ""
                    echo "# charm-crypto library paths (added by install.sh)"
                    echo "set -gx ${LIB_VAR} ${PREFIX}/lib \$${LIB_VAR}"
                } >> "$SHELL_RC"
            else
                # POSIX-compatible shells (bash, zsh, sh)
                local ENV_LINE="export ${LIB_VAR}=${PREFIX}/lib:\$${LIB_VAR}"
                {
                    echo ""
                    echo "# charm-crypto library paths (added by install.sh)"
                    echo "$ENV_LINE"
                } >> "$SHELL_RC"
            fi
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
    local BOLD='\033[1m'
    local RESET='\033[0m'
    echo -e "${BOLD}Charm-Crypto Installation Script v${CHARM_VERSION}${RESET}"
    echo ""
    echo -e "${BOLD}Supported Platforms:${RESET}"
    cat << EOF
  - Ubuntu/Debian (and derivatives: Linux Mint, Pop!_OS)
  - Fedora/RHEL/CentOS (and derivatives: Rocky, Alma, Oracle Linux)
  - Arch Linux (and derivatives: Manjaro, EndeavourOS, Artix)
  - macOS (Intel and Apple Silicon)

EOF
    echo -e "${BOLD}Usage:${RESET} $0 [OPTIONS]"
    echo ""
    echo -e "${BOLD}Options:${RESET}"
    cat << EOF
  --from-pypi     Install from PyPI (default, recommended)
  --from-source   Clone and build from source
  --deps-only     Only install system dependencies and PBC
  --no-sudo       Don't use sudo (for containers/CI)
  --prefix=PATH   Installation prefix (default: /usr/local)
  --python=PATH   Path to Python interpreter
  --help, -h      Show this help message

EOF
    echo -e "${BOLD}Examples:${RESET}"
    cat << EOF
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

