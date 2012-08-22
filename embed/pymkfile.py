
import distutils.sysconfig
import string, sys

configopts = {}

maketemplate = """
PYLIB=%(pythonlib)s
PYINC=-I%(pythoninc)s
LIBS=%(pylibs)s
OPTS=%(pyopt)s
PROGRAMS=%(programs)s
all: $(PROGRAMS)
"""

configopts['pythonlib'] = distutils.sysconfig.get_config_var('LIBPL') \
+ '/' + \
distutils.sysconfig.get_config_var('LIBRARY')
configopts['pythoninc'] = ''
configopts['pylibs'] = ''
for dir in (distutils.sysconfig.get_config_var('INCLDIRSTOMAKE')).split():
	configopts['pythoninc'] += '-I%s ' % (dir,)
for dir in (distutils.sysconfig.get_config_var('LIBDIR')).split():
	configopts['pylibs'] += '-L%s ' % (dir,)

configopts['pylibs'] += distutils.sysconfig.get_config_var('MODLIBS') \
			+ ' ' + \
			distutils.sysconfig.get_config_var('LIBS') \
			+ ' ' + \
			distutils.sysconfig.get_config_var('SYSLIBS')
configopts['pyopt'] = distutils.sysconfig.get_config_var('OPT')

targets = ''
for arg in sys.argv[1:]:
	targets += arg + ' '
configopts['programs'] = targets

print(maketemplate % configopts)

for arg in sys.argv[1:]:
	print("%s: %s.o\n\tgcc %s.o $(LIBS) $(PYLIB) -o %s" \
		% (arg, arg, arg, arg))
	print("%s.o: %s.c\n\tgcc %s.c -c $(PYINC) $(OPTS)" \
		% (arg, arg, arg))

print("clean:\n\trm -f $(PROGRAMS) *.o *.pyc core")
