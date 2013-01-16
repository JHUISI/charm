include ../config.mk

INCLUDES += -I. -I.. -I../$(underlib)

objects := util.o SecretUtil.o policy.tab.o

.PHONY: all
all: $(objects)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

policy.tab.o: policy.y
	bison policy.y
	$(CC) $(CFLAGS) $(INCLUDES) -c policy.tab.c -o $@

clean:
	rm -f *.o
