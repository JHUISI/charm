#!/bin/bash
#Using the android port: https://github.com/guardianproject/openssl-android
#It looks like android-python is compiling openssl anyway. We should used theirs

exit


export BD="/home/charm/android-python27/android-python27/python-build-brandon-clean"
export NDK="$BD/android-ndk-r8e"

$NDK/ndk-build
