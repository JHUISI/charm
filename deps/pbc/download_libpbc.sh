#!/bin/sh

REPO=https://crypto.stanford.edu/pbc/files
PBC=pbc
VERSION=$1

if [ ${VERSION} = "" ]; then
    echo "Missing ${PBC} version to download."
    exit 1
fi

if [ -f "${PBC}-${VERSION}.tar.gz" ]; then
    echo "Found: ${PBC}-${VERSION}.tar.gz. Delete first if updating."
    exit 0
fi

wget ${REPO}/${PBC}-${VERSION}.tar.gz
exit 0
