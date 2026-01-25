.. _platform-install-manual:

Platform Install Manual
=======================

This guide provides installation instructions for building Charm-Crypto from source
on various platforms. Charm automates much of the build process through its configure
and make scripts.

If you encounter any issues not covered here, please contact us at jakinye3@jhu.edu.

Dependencies
------------

The following dependencies are required to build Charm:

+-------------+------------------+----------+------------------------------------------+
| Dependency  | Version          | Required | Notes                                    |
+=============+==================+==========+==========================================+
| Python      | 3.8+             | Yes      | Python 2.x is not supported              |
+-------------+------------------+----------+------------------------------------------+
| GMP         | 5.x+             | Yes      | GNU Multiple Precision Arithmetic Library|
+-------------+------------------+----------+------------------------------------------+
| PBC         | 1.0.0            | Yes      | Pairing-Based Cryptography library       |
+-------------+------------------+----------+------------------------------------------+
| OpenSSL     | 1.x or 3.x       | Yes      | Cryptographic library                    |
+-------------+------------------+----------+------------------------------------------+
| pyparsing   | >=2.1.5, <2.4.1  | Yes      | Python parsing library                   |
+-------------+------------------+----------+------------------------------------------+
| pytest      | latest           | Testing  | For running test suite                   |
+-------------+------------------+----------+------------------------------------------+

Optional dependencies:

- **MIRACL** - See :ref:`charm-with-miracl` if interested.
- **RELIC** - See :ref:`charm-with-relic` if interested.

Run ``./configure.sh --help`` for all available configuration options.

Source Code
-----------

Clone the latest version from GitHub::

    git clone https://github.com/JHUISI/charm.git
    cd charm

Building on Linux
-----------------

The Charm build process is managed through configure and make scripts.
The general workflow for all Linux distributions is:

1. Install system dependencies via package manager
2. Build and install PBC 1.0.0 from source
3. Configure Charm
4. Build and install Charm
5. Verify installation

Ubuntu/Debian (22.04 LTS, 24.04 LTS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These instructions work for Ubuntu 22.04, 24.04, and recent Debian versions.

**Step 1: Install build tools and dependencies**

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install -y build-essential flex bison wget m4 \
        python3 python3-dev python3-setuptools python3-pip python3-venv \
        libgmp-dev libssl-dev

**Step 2: Build and install PBC 1.0.0**

.. code-block:: bash

    wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
    tar xzf pbc-1.0.0.tar.gz
    cd pbc-1.0.0
    ./configure LDFLAGS="-lgmp"
    make
    sudo make install
    sudo ldconfig
    cd ..

**Step 3: Set up Python environment and install dependencies**

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate
    pip install 'pyparsing>=2.1.5,<2.4.1' pytest hypothesis

**Step 4: Configure and build Charm**

.. code-block:: bash

    ./configure.sh
    make
    sudo make install
    sudo ldconfig

**Step 5: Verify installation**

.. code-block:: bash

    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
    python -c "from charm.toolbox.pairinggroup import PairingGroup; print('Success!')"

**Step 6: Run tests (optional)**

.. code-block:: bash

    make test

Fedora/RHEL/CentOS
^^^^^^^^^^^^^^^^^^

These instructions work for Fedora 38+, RHEL 8+, CentOS Stream, Rocky Linux, and AlmaLinux.

**Step 1: Install build tools and dependencies**

.. code-block:: bash

    # Use 'yum' instead of 'dnf' on older systems (RHEL 7, CentOS 7)
    sudo dnf install -y gcc gcc-c++ make flex bison wget m4 \
        python3 python3-devel python3-pip \
        gmp-devel openssl-devel

**Step 2: Build and install PBC 1.0.0**

.. code-block:: bash

    wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
    tar xzf pbc-1.0.0.tar.gz
    cd pbc-1.0.0
    ./configure LDFLAGS="-lgmp"
    make
    sudo make install
    sudo ldconfig
    cd ..

**Step 3: Set up Python environment and install dependencies**

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate
    pip install 'pyparsing>=2.1.5,<2.4.1' pytest hypothesis

**Step 4: Configure and build Charm**

.. code-block:: bash

    ./configure.sh
    make
    sudo make install
    sudo ldconfig

**Step 5: Verify installation**

.. code-block:: bash

    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
    python -c "from charm.toolbox.pairinggroup import PairingGroup; print('Success!')"

Arch Linux
^^^^^^^^^^

**Step 1: Install build tools and dependencies**

.. code-block:: bash

    sudo pacman -S base-devel wget m4 python python-setuptools python-pip gmp openssl

**Step 2: Build and install PBC 1.0.0**

.. code-block:: bash

    wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
    tar xzf pbc-1.0.0.tar.gz
    cd pbc-1.0.0
    ./configure LDFLAGS="-lgmp"
    make
    sudo make install
    sudo ldconfig
    cd ..

**Step 3: Set up Python environment and install dependencies**

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate
    pip install 'pyparsing>=2.1.5,<2.4.1' pytest hypothesis

**Step 4: Configure and build Charm**

.. code-block:: bash

    ./configure.sh
    make
    sudo make install
    sudo ldconfig

**Step 5: Verify installation**

.. code-block:: bash

    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
    python -c "from charm.toolbox.pairinggroup import PairingGroup; print('Success!')"

Building on Windows
-------------------

The recommended approach for building Charm on Windows is to use Windows Subsystem
for Linux 2 (WSL2), which provides a full Linux environment.

Windows with WSL2 (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

WSL2 is available on Windows 10 version 2004+ and Windows 11.

**Step 1: Install WSL2 with Ubuntu**

Open PowerShell as Administrator and run:

.. code-block:: powershell

    wsl --install -d Ubuntu

Restart your computer when prompted, then open Ubuntu from the Start menu.

**Step 2: Follow Ubuntu/Debian instructions**

Once inside WSL2, follow the :ref:`Ubuntu/Debian installation instructions <platform-install-manual>` above.

.. note::

    WSL2 provides near-native Linux performance and full compatibility with Charm.
    This is the recommended approach for Windows development.

Building on macOS
-----------------

macOS requires Homebrew for dependency management. Instructions are provided for
both Intel and Apple Silicon (M1/M2/M3) Macs.

macOS with Homebrew (Intel and Apple Silicon)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Step 1: Install Homebrew** (if not already installed)

.. code-block:: bash

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

**Step 2: Install build tools and dependencies**

.. code-block:: bash

    brew install gmp openssl@3 wget python@3

**Step 3: Build and install PBC 1.0.0**

.. code-block:: bash

    wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
    tar xzf pbc-1.0.0.tar.gz
    cd pbc-1.0.0
    ./configure LDFLAGS="-lgmp"
    make
    sudo make install
    cd ..

**Step 4: Set up Python environment and install dependencies**

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate
    pip install 'pyparsing>=2.1.5,<2.4.1' pytest hypothesis

**Step 5: Configure and build Charm**

For Intel Macs:

.. code-block:: bash

    ./configure.sh --enable-darwin
    make
    sudo make install

For Apple Silicon (M1/M2/M3) Macs:

.. code-block:: bash

    export CFLAGS="-I/opt/homebrew/include"
    export LDFLAGS="-L/opt/homebrew/lib"
    ./configure.sh --enable-darwin
    make
    sudo make install

**Step 6: Verify installation**

.. code-block:: bash

    export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH
    python -c "from charm.toolbox.pairinggroup import PairingGroup; print('Success!')"

.. note::

    The ``--enable-darwin`` flag is required for all macOS builds to handle
    macOS-specific compiler and library path configurations.

Generic Unix (Building All Dependencies from Source)
----------------------------------------------------

For systems without package managers or with outdated packages, you can build
all dependencies from source.

**Step 1: Build GMP**

.. code-block:: bash

    wget https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz
    tar xf gmp-6.3.0.tar.xz
    cd gmp-6.3.0
    ./configure --enable-shared
    make
    sudo make install
    cd ..

**Step 2: Build OpenSSL** (if not available or outdated)

.. code-block:: bash

    wget https://www.openssl.org/source/openssl-3.0.12.tar.gz
    tar xzf openssl-3.0.12.tar.gz
    cd openssl-3.0.12
    ./config shared
    make
    sudo make install
    cd ..

**Step 3: Build PBC 1.0.0**

.. code-block:: bash

    wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
    tar xzf pbc-1.0.0.tar.gz
    cd pbc-1.0.0
    ./configure LDFLAGS="-lgmp"
    make
    sudo make install
    cd ..

**Step 4: Update library cache**

.. code-block:: bash

    sudo ldconfig

**Step 5: Continue with Charm installation**

Follow Steps 3-5 from the Ubuntu/Debian section above.

Troubleshooting
---------------

This section covers common issues encountered during installation.

Library not found errors
^^^^^^^^^^^^^^^^^^^^^^^^

If you see errors like ``ImportError: libpbc.so.1: cannot open shared object file``:

**On Linux:**

.. code-block:: bash

    # Add to your shell profile (~/.bashrc or ~/.zshrc)
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

    # Update the library cache
    sudo ldconfig

**On macOS:**

.. code-block:: bash

    # Add to your shell profile (~/.zshrc or ~/.bash_profile)
    export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH

Header not found on macOS Apple Silicon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you see errors about missing headers on M1/M2/M3 Macs:

.. code-block:: bash

    export CFLAGS="-I/opt/homebrew/include"
    export LDFLAGS="-L/opt/homebrew/lib"
    ./configure.sh --enable-darwin

This is needed because Homebrew installs to ``/opt/homebrew`` on Apple Silicon
instead of ``/usr/local`` on Intel Macs.

pyparsing version conflicts
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Charm requires a specific version range of pyparsing:

.. code-block:: bash

    pip install 'pyparsing>=2.1.5,<2.4.1'

If you have a newer version installed, you may need to create a virtual environment:

.. code-block:: bash

    python3 -m venv charm-env
    source charm-env/bin/activate
    pip install 'pyparsing>=2.1.5,<2.4.1'

PBC build fails with GMP errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If PBC fails to build with GMP-related errors:

.. code-block:: bash

    # Ensure GMP is installed and use explicit LDFLAGS
    ./configure LDFLAGS="-lgmp" CPPFLAGS="-I/usr/local/include"
    make clean
    make

Permission denied errors
^^^^^^^^^^^^^^^^^^^^^^^^

If you get permission errors during ``make install``:

.. code-block:: bash

    # Use sudo for system-wide installation
    sudo make install

    # Or install to user directory (add --prefix to configure)
    ./configure.sh --prefix=$HOME/.local
    make
    make install

Running Tests
-------------

After installation, verify everything works by running the test suite:

.. code-block:: bash

    # Run all tests
    make test

    # Run scheme tests only
    make test-schemes

    # Run toolbox tests only
    make test-charm

    # Use pytest directly for more options
    pytest -v

Advanced Pairing Libraries
--------------------------

For advanced users who want to use alternative pairing libraries:

.. toctree::
   :maxdepth: 1

   miracl
   relic

Deprecated
----------

.. toctree::
   :maxdepth: 1

   mobile
