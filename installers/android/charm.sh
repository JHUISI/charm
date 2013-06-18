#!/bin/bash

export BD="$BD"

export NDK="$BD/android-ndk-r8e"
export SDK="$BD/android-sdk-linux/"
export NDKPLATFORM="$NDK/platforms/android-9/arch-arm"
export PATH="$NDK/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/:$SDK/tools:$PATH"
export CHARM_ANDROID="yes"

export PYTHONPATH="$PYTHONPATH:$BD/python-for-android/python-build/python-libs/py4a"
export PY4A_INC="$BD/android-python27/python-build/"
export PY4A_LIB="$BD/android-python27/python-build/Python"

INC="$NDKPLATFORM/usr/include:$BD/obj/include:$PY4A_INC/Python/Include"
LIB="$BD/obj/lib:$PY4A_INC/obj/obj/local/armeabi"

PBC_INC=$BD/pbc/include
SSL_INC=$PY4A_INC/openssl/include/

export SYSROOT="$NDK/platforms/android-9/arch-arm"
export CFLAGS=" --sysroot=$SYSROOT"

./configure.sh
echo "BUILD_ANDROID=yes">>config.mk
python setup.py build_ext -I ../Python:../Python/Include:../include:charm/core/utilities:charm/core/benchmark:$GMP_INC:$PBC_INC:$SSL_INC:$INC -L $LIB bdist_egg --plat-name=linux-armv 
