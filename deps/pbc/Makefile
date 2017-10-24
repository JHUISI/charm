.PHONY: all clean

include ../../config.mk

VERSION := 0.5.14
LIBPBC := pbc-${VERSION}

all: get_pbc ${LIBPBC}/.built

${LIBPBC}/.built: ${LIBPBC}
	echo "[+] Building ${LIBPBC}"; \
	cd $<; \
	./configure --prefix=$(prefix) && \
	make && \
	sudo make install && \
	touch .built

${LIBPBC}: ${LIBPBC}.tar.gz
	tar -xf $^

get_pbc:
	./download_libpbc.sh ${VERSION}

clean:
	rm -rf ${LIBPBC}

distclean:
	rm -rf ${LIBPBC} ${LIBPBC}.tar.gz
