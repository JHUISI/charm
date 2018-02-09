#!/bin/bash

#in python-build/functions.sh I was getting syntax errors. The offending lines were:
#   function downloader { curl -LO "$1" ; }
#   function downloader { wget -LO "$1" ; }
#deletung the semicolon in these lines fixes the problem


export BD="$BD"
export NDK="$BD/android-ndk-r8e"
export SDK="$BD/android-sdk-linux_x86/"
export NDKPLATFORM="$NDK/platforms/android-9/arch-arm"
export PATH="$NDK/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/:$NDK:$SDK/tools:$PATH"

cd python-build
chmod +x *.sh
bash ./bootstrap.sh && ./build.sh && ./package.sh
