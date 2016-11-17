.PHONY: all clean

include ../../config.mk

VERSION=toolkit-0.4.1a
BN_254_CURVE=bn254
BN_256_CURVE=bn256
SS_1536_CURVE=ss1536

all: get_relic relic-$(VERSION)/.built

relic-$(VERSION)/.built: relic-${VERSION}
	./build_configs.py --src $< -p $(prefix) -c bn -s 254 -t; \
	./build_configs.py --src $< -p $(prefix) -c bn -s 256 -t; \
	./build_configs.py --src $< -p $(prefix) -c ss -s 1536 -t; \
	sed -i -e '/^#define VERSION/d' $(prefix)/include/relic_$(BN_254_CURVE)/relic_conf.h && \
	sed -i -e '/^#define ep2_mul/i \
//#define ep2_mul' $(prefix)/include/relic_$(BN_254_CURVE)/relic_label.h && \
	sed -i -e '/^#define VERSION/d' $(prefix)/include/relic_$(BN_256_CURVE)/relic_conf.h && \
	sed -i -e '/^#define ep2_mul/i \
//#define ep2_mul' $(prefix)/include/relic_$(BN_256_CURVE)/relic_label.h && \
	sed -i -e '/^#define VERSION/d' $(prefix)/include/relic_$(SS_1536_CURVE)/relic_conf.h && \
	sed -i -e '/^#define ep2_mul/i \
//#define ep2_mul' $(prefix)/include/relic_$(SS_1536_CURVE)/relic_label.h && \
	./run_install_clean.sh $(prefix) && \
	touch ./$@

relic-$(VERSION): relic-$(VERSION).tar.gz
	tar xf $^

get_relic:
	./get_relic_source.sh

clean:
	rm -rf relic-$(VERSION)

distclean:
	rm -rf relic-toolkit*
