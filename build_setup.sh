#!/bin/bash

export CFLAGS="-I/opt/homebrew/include -I/opt/homebrew/opt/gmp/include -I/opt/homebrew/opt/openssl@3/include"
export CPPFLAGS="$CFLAGS"
export LDFLAGS="-L/opt/homebrew/lib -L/opt/homebrew/opt/gmp/lib -L/opt/homebrew/opt/openssl@3/lib"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/gmp/lib/pkgconfig:/opt/homebrew/opt/openssl@3/lib/pkgconfig:/opt/homebrew/opt/pbc/lib/pkgconfig"
# (Optional, helps some setups)
export CPATH="/opt/homebrew/include:/opt/homebrew/opt/gmp/include:/opt/homebrew/opt/openssl@3/include"
export LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/gmp/lib:/opt/homebrew/opt/openssl@3/lib"

make
