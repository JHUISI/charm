CONFIG_FILE=../config.mk
include ${CONFIG_FILE}

# Get Python library from python-config
PY_LIB=$(shell python3-config --ldflags --embed 2>/dev/null || python3-config --ldflags)
LIBS=-L/usr/local/lib -L/opt/local/lib -lpthread -ldl -lutil -lm -lgmp -lpbc ${PY_LIB}
OPTS=-DDYNAMIC_ANNOTATIONS_ENABLED=1 -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes

# Include CPPFLAGS for GMP/OpenSSL headers from config.mk
CFLAGS+=${PY_CFLAGS} ${CPPFLAGS}

LDFLAGS+=${PY_LDFLAGS}
LDFLAGS+=${LIBS}

PROGRAMS=test
OBJECTS=charm_embed_api.o test.o
all: $(PROGRAMS)

test: ${OBJECTS}
	${CC} ${OBJECTS} ${CFLAGS} ${LDFLAGS} ${OPTS} -o test

charm_embed_api.o: charm_embed_api.c
	${CC} ${CFLAGS} $(OPTS) -c charm_embed_api.c

test.o: test.c
	${CC} ${CFLAGS} $(OPTS) test.c -c 

clean:
	rm -f $(PROGRAMS) *.o *.pyc core
