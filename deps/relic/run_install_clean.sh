#!/bin/bash

ORACLE_RELEASE=/etc/oracle-release
SYSTEM_RELEASE=/etc/system-release
DEBIAN_VERSION=/etc/debian_version
SERVER_ONLY="no"

function console() {
  echo "[+] $1"
}

function fail() {
  echo "[!] $1"
  exit 1
}

function platform() {
  local  __out=$1
  if [[ -f "$LSB_RELEASE" ]] && grep -q 'DISTRIB_ID=Ubuntu' $LSB_RELEASE; then
    FAMILY="debian"
    eval $__out="ubuntu"
  elif [[ -f "$DEBIAN_VERSION" ]]; then
    FAMILY="debian"
    eval $__out="debian"
  else
    eval $__out=`uname -s | tr '[:upper:]' '[:lower:]'`
  fi
}

function distro() {
  local __out=$2
  if [[ $1 = "ubuntu" ]]; then
    eval $__out=`awk -F= '/DISTRIB_CODENAME/ { print $2 }' $LSB_RELEASE`
  elif [[ $1 = "darwin" ]]; then
    eval $__out=`sw_vers -productVersion | awk -F '.' '{print $1 "." $2}'`
  elif [[ $1 = "debian" ]]; then
    eval $__out="`lsb_release -cs`"
  else
    eval $__out="unknown_version"
  fi
}

PREFIX=$1
RELIC_LIB=$PREFIX/lib/librelic

function main() {
  platform OS
  distro $OS OS_VERSION

  if [[ $1 = "get_platform" ]]; then
    printf "OS:\t$OS\n"
    printf "VER:\t$OS_VERSION\n"
    return 0
  fi

  if [[ $OS = "darwin" ]]; then
    console "Detected Mac OS X ($OS_VERSION)"
    set -x
    install_name_tool -id ${RELIC_LIB}_bn254.dylib ${RELIC_LIB}_bn254.dylib
    install_name_tool -id ${RELIC_LIB}_bn256.dylib ${RELIC_LIB}_bn256.dylib
    install_name_tool -id ${RELIC_LIB}_ss1536.dylib ${RELIC_LIB}_ss1536.dylib
    set +x
  fi
}

main $1

