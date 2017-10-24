include ../config.mk

.PHONY: all clean

# relic openssl pbc
DIRS=relic pbc
all: $(DIRS)
	for d in $(DIRS); do \
		make -C $$d; \
	done

clean: $(DIRS)
	rm -rf root
	for d in $(DIRS); do \
		make -C $$d clean; \
	done
