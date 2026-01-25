# Charm-Crypto Embed API Makefile
# Cross-platform build for macOS, Linux, and Windows (MinGW/MSYS2)

CONFIG_FILE=../config.mk
include ${CONFIG_FILE}

# ============================================================================
# Platform Detection
# ============================================================================
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)
UNAME_M := $(shell uname -m 2>/dev/null || echo x86_64)

# ============================================================================
# Python Configuration
# ============================================================================
# Get Python library flags - try --embed first (Python 3.8+), fall back to older style
PY_LIB := $(shell python3-config --ldflags --embed 2>/dev/null || python3-config --ldflags 2>/dev/null)
PY_INC := $(shell python3-config --includes 2>/dev/null)

# ============================================================================
# Platform-Specific Settings
# ============================================================================
ifeq ($(UNAME_S),Darwin)
    # macOS (both Intel and Apple Silicon)
    PLATFORM := macos

    # Detect architecture for library paths
    ifeq ($(UNAME_M),arm64)
        # Apple Silicon (M1/M2/M3) - Homebrew installs to /opt/homebrew
        HOMEBREW_PREFIX ?= /opt/homebrew
    else
        # Intel Mac - Homebrew installs to /usr/local
        HOMEBREW_PREFIX ?= /usr/local
    endif

    # Library paths for macOS
    PLATFORM_LDFLAGS := -L$(HOMEBREW_PREFIX)/lib -L/usr/local/lib
    PLATFORM_CFLAGS := -I$(HOMEBREW_PREFIX)/include -I/usr/local/include

    # macOS-specific libraries
    PLATFORM_LIBS := -lpthread -ldl -lm -lgmp -lpbc

    # Framework for Python on macOS
    ifneq (,$(findstring -framework,$(PY_LIB)))
        PLATFORM_LIBS += $(PY_LIB)
    else
        PLATFORM_LIBS += $(PY_LIB)
    endif

    # Executable suffix
    EXESUF :=

else ifeq ($(UNAME_S),Linux)
    # Linux (Ubuntu/Debian/RHEL/etc.)
    PLATFORM := linux

    # Standard library paths for Linux
    PLATFORM_LDFLAGS := -L/usr/local/lib -L/usr/lib
    PLATFORM_CFLAGS := -I/usr/local/include -I/usr/include

    # Linux-specific libraries
    PLATFORM_LIBS := -lpthread -ldl -lutil -lm -lgmp -lpbc $(PY_LIB)

    # Add rpath for finding shared libraries at runtime
    PLATFORM_LDFLAGS += -Wl,-rpath,/usr/local/lib

    # Executable suffix
    EXESUF :=

else ifneq (,$(findstring MINGW,$(UNAME_S)))
    # Windows (MinGW/MSYS2)
    PLATFORM := windows

    # MSYS2/MinGW paths
    MINGW_PREFIX ?= /mingw64

    # Library paths for Windows
    PLATFORM_LDFLAGS := -L$(MINGW_PREFIX)/lib -L/c/charm-crypto/lib
    PLATFORM_CFLAGS := -I$(MINGW_PREFIX)/include -I/c/charm-crypto/include

    # Windows-specific libraries
    PLATFORM_LIBS := -lm -lgmp -lpbc $(PY_LIB) -lws2_32

    # Executable suffix
    EXESUF := .exe

else ifneq (,$(findstring MSYS,$(UNAME_S)))
    # Windows (MSYS2)
    PLATFORM := windows
    MINGW_PREFIX ?= /mingw64
    PLATFORM_LDFLAGS := -L$(MINGW_PREFIX)/lib
    PLATFORM_CFLAGS := -I$(MINGW_PREFIX)/include
    PLATFORM_LIBS := -lm -lgmp -lpbc $(PY_LIB) -lws2_32
    EXESUF := .exe

else
    # Unknown platform - try generic settings
    PLATFORM := unknown
    PLATFORM_LDFLAGS := -L/usr/local/lib
    PLATFORM_CFLAGS := -I/usr/local/include
    PLATFORM_LIBS := -lpthread -ldl -lm -lgmp -lpbc $(PY_LIB)
    EXESUF :=
endif

# ============================================================================
# Compiler Settings
# ============================================================================
# Use CC from config.mk or default to gcc
CC ?= gcc

# Optimization and warning flags
OPTS := -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes

# Combine all flags
# Include paths: Python headers + GMP/OpenSSL from config.mk + platform-specific
ALL_CFLAGS := $(CFLAGS) $(PY_CFLAGS) $(PY_INC) $(CPPFLAGS) $(PLATFORM_CFLAGS) $(OPTS)

# Library paths and libraries
ALL_LDFLAGS := $(LDFLAGS) $(PY_LDFLAGS) $(PLATFORM_LDFLAGS) $(PLATFORM_LIBS)

# ============================================================================
# Build Targets
# ============================================================================
PROGRAMS := test$(EXESUF)
OBJECTS := charm_embed_api.o test.o

.PHONY: all clean info

all: $(PROGRAMS)

# Link the test executable
$(PROGRAMS): $(OBJECTS)
	@echo "Linking $(PROGRAMS) for $(PLATFORM) ($(UNAME_M))..."
	$(CC) $(OBJECTS) $(ALL_CFLAGS) $(ALL_LDFLAGS) -o $(PROGRAMS)
	@echo "Build complete: $(PROGRAMS)"

# Compile the embed API
charm_embed_api.o: charm_embed_api.c charm_embed_api.h
	@echo "Compiling charm_embed_api.c..."
	$(CC) $(ALL_CFLAGS) -c charm_embed_api.c -o charm_embed_api.o

# Compile the test program
test.o: test.c charm_embed_api.h
	@echo "Compiling test.c..."
	$(CC) $(ALL_CFLAGS) -c test.c -o test.o

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(PROGRAMS) *.o *.pyc core *.exe
ifeq ($(PLATFORM),macos)
	rm -rf *.dSYM
endif

# Display build configuration (useful for debugging)
info:
	@echo "============================================"
	@echo "Charm Embed API Build Configuration"
	@echo "============================================"
	@echo "Platform:        $(PLATFORM)"
	@echo "Architecture:    $(UNAME_M)"
	@echo "Compiler:        $(CC)"
	@echo "Executable:      $(PROGRAMS)"
	@echo ""
	@echo "CFLAGS:          $(ALL_CFLAGS)"
	@echo ""
	@echo "LDFLAGS:         $(ALL_LDFLAGS)"
	@echo ""
	@echo "Python config:   $(PY_INC)"
	@echo "Python libs:     $(PY_LIB)"
ifeq ($(PLATFORM),macos)
	@echo "Homebrew prefix: $(HOMEBREW_PREFIX)"
endif
	@echo "============================================"
