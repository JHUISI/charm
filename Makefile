
CONFIG=config.mk
include ./${CONFIG}
export CONFIG_FILE=${CURDIR}/${CONFIG}

# user config options
setup1=$(shell mkdir -p /tmp/build-charm)
dest_build=/tmp/build-charm

help:
	@echo "make deps - Build dependency libs locally."
	@echo "make source - Create source package."
	@echo "make install - Install on local system."
	@echo "make clean - Get rid of scratch and byte files."
	@echo "make test  - Run Unit Tests."
	@echo "make xmltest  - Run Unit Tests and produce xml results in folder test-results."
	@echo "make doc   - Compile documentation"

.PHONY: setup
setup:
	@echo "Setup build/staging directories"
	set -x
	${setup1}
	set +x

.PHONY: all
all: setup 
	@echo "Building the Charm Framework"
	${PYTHON} setup.py build ${PYTHONFLAGS} ${PYTHONBUILDEXT}
	@echo "Complete"

.PHONY: deps
deps:
	@echo "Building the dependency libs"
	make -C deps

.PHONY: source
source:
	$(PYTHON) setup.py sdist --formats=gztar,zip # --manifest-only

.PHONY: install
install:
	$(PYTHON) setup.py install

.PHONY: uninstall
uninstall:
	$(PYTHON) setup.py uninstall
	
.PHONY: test
test:
	$(PYTHON) setup.py test

.PHONY: test-schemes
test-schemes:
	$(PYTHON) -m unittest discover -p "*_test.py"  schemes/test/
	find . -name '*.pyc' -delete

.PHONY: test-charm
test-charm:
	$(PYTHON) -m unittest discover -p "*_test.py"  charm/test/toolbox/
	find . -name '*.pyc' -delete

.PHONY: xmltest 
xmltest:
	$(PYTHON) tests/all_tests_with_xml_test_result.py
	find . -name '*.pyc' -delete

.PHONY: doc
doc:
	if test "${BUILD_DOCS}" = "yes" ; then \
	${MAKE} -C doc html; \
	fi

# .PHONY: buildrpm
# buildrpm:
#        $(PYTHON) setup.py bdist_rpm # --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

.PHONY: builddeb
builddeb:
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist --dist-dir=../ --prune
	#rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	#dpkg-buildpackage -i -I -rfakeroot

.PHONY: clean
clean:
	$(PYTHON) setup.py clean
#	cd doc; $(MAKE) clean
#        $(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf build/ dist/ ${dest_build} MANIFEST
	rm ${CONFIG}
	find . -name '*.pyc' -delete
	find . -name '*.so' -delete 
	find . -name '*.o' -delete 
	find . -name '*.dll' -delete 


