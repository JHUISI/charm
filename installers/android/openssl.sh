#!/bin/bash
#Using the android port: https://github.com/guardianproject/openssl-android
#It looks like android-python is compiling openssl anyway. We should used theirs

exit


export BD="$BD"
export NDK="$BD/android-ndk-r8e"

$NDK/ndk-build
