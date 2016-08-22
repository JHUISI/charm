#!/bin/sh

GIT_VERSION=0.4.1
VERSION=0.4.1a
FORMAT=tar.gz
LINK=https://github.com/relic-toolkit/relic
RELIC=relic-toolkit

if [ -f "${RELIC}-${VERSION}.tar.gz" ]; then
    echo "Found: ${RELIC}-${VERSION}.tar.gz. Delete first if updating."
fi

echo "Clone github repo @ ${LINK}"
if [ -d "${RELIC}-${GIT_VERSION}.git" ]; then
    cd ${RELIC}-${GIT_VERSION}.git
    git pull
else
    git clone ${LINK} ${RELIC}-${GIT_VERSION}.git
    cd ${RELIC}-${GIT_VERSION}.git
fi

echo "Create archive of source (without git files)"
git archive --format ${FORMAT} --output ../${RELIC}-${VERSION}.test.${FORMAT} HEAD

echo "Create final tarball: ${RELIC}-${VERSION}.${FORMAT}"
cd ..
mkdir ${RELIC}-${VERSION}
cd ${RELIC}-${VERSION}
tar -xf ../${RELIC}-${VERSION}.test.${FORMAT}

echo "Fix symbols..."
grep -rl "BN_BITS" ./ | xargs sed -i 's/BN_BITS/RLC_BN_BITS/g'
grep -rl "BN_BYTES" ./ | xargs sed -i 's/BN_BYTES/RLC_BN_BYTES/g'

grep -rl "MIN" ./ | xargs sed -i 's/MIN/RLC_MIN/g'
grep -rl "MAX" ./ | xargs sed -i 's/MAX/RLC_MAX/g'
grep -rl "ALIGN" ./ | xargs sed -i 's/ALIGN/RLC_ALIGN/g'
grep -rl "rsa_t" ./ | xargs sed -i 's/rsa_t/rlc_rsa_t/g'
grep -rl "rsa_st" ./ | xargs sed -i 's/rsa_st/rlc_rsa_st/g'
sed -i -e '/^#define ep2_mul /d' include/relic_label.h

cd ..
tar -czf ${RELIC}-${VERSION}.tar.gz ${RELIC}-${VERSION}
rm ${RELIC}-${VERSION}.test.${FORMAT}
rm -r ${RELIC}-${VERSION}
