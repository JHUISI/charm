
CONFIG=config.mk
include ./${CONFIG}
export CONFIG_FILE=${CURDIR}/${CONFIG}

# user config options
setup1=$(shell mkdir -p /tmp/build-charm)
dest_build=/tmp/build-charm

help:
	@echo "Build targets:"
	@echo "  make deps      - Build dependency libs locally."
	@echo "  make source    - Create source package."
	@echo "  make install   - Install on local system."
	@echo "  make clean     - Get rid of scratch and byte files."
	@echo "  make doc       - Compile documentation"
	@echo ""
	@echo "Test targets:"
	@echo "  make test           - Run all tests via pytest (same as test-all)"
	@echo "  make test-unit      - Run unit tests only (toolbox, serialize, vectors)"
	@echo "  make test-schemes   - Run cryptographic scheme tests only"
	@echo "  make test-toolbox   - Run toolbox tests only"
	@echo "  make test-zkp       - Run ZKP compiler tests only"
	@echo "  make test-adapters  - Run adapter tests only"
	@echo "  make test-all       - Run all test categories sequentially"
	@echo "  make test-embed     - Build and run C/C++ embedding API tests"
	@echo "  make xmltest        - Run tests and produce XML results"

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

# Test category targets
.PHONY: test-unit
test-unit:
	@echo "========================================"
	@echo "Running Unit Tests (toolbox, serialize, vectors)"
	@echo "========================================"
	$(PYTHON) -m pytest charm/test/toolbox/ charm/test/serialize/ charm/test/vectors/ -v
	@find . -name '*.pyc' -delete
	@echo "Unit tests complete."

.PHONY: test-schemes
test-schemes:
	@echo "========================================"
	@echo "Running Scheme Tests"
	@echo "========================================"
	$(PYTHON) -m pytest charm/test/schemes/ -v
	@find . -name '*.pyc' -delete
	@echo "Scheme tests complete."

.PHONY: test-toolbox
test-toolbox:
	@echo "========================================"
	@echo "Running Toolbox Tests"
	@echo "========================================"
	$(PYTHON) -m pytest charm/test/toolbox/ -v
	@find . -name '*.pyc' -delete
	@echo "Toolbox tests complete."

.PHONY: test-zkp
test-zkp:
	@echo "========================================"
	@echo "Running ZKP Compiler Tests"
	@echo "========================================"
	$(PYTHON) -m pytest charm/test/zkp_compiler/ -v
	@find . -name '*.pyc' -delete
	@echo "ZKP compiler tests complete."

.PHONY: test-adapters
test-adapters:
	@echo "========================================"
	@echo "Running Adapter Tests"
	@echo "========================================"
	$(PYTHON) -m pytest charm/test/adapters/ -v
	@find . -name '*.pyc' -delete
	@echo "Adapter tests complete."

.PHONY: test-integration
test-integration:
	@echo "========================================"
	@echo "Running Integration Tests"
	@echo "========================================"
	@echo "Note: Integration tests run benchmark and cross-module tests"
	$(PYTHON) -m pytest charm/test/benchmark/ -v --ignore=charm/test/fuzz/
	@find . -name '*.pyc' -delete
	@echo "Integration tests complete."

.PHONY: test-all
test-all:
	@echo "========================================"
	@echo "Running All Test Categories"
	@echo "========================================"
	@echo ""
	@echo ">>> [1/6] Unit Tests (toolbox, serialize, vectors)"
	$(PYTHON) -m pytest charm/test/toolbox/ charm/test/serialize/ charm/test/vectors/ -v
	@echo ""
	@echo ">>> [2/6] Scheme Tests"
	$(PYTHON) -m pytest charm/test/schemes/ -v
	@echo ""
	@echo ">>> [3/6] ZKP Compiler Tests"
	$(PYTHON) -m pytest charm/test/zkp_compiler/ -v
	@echo ""
	@echo ">>> [4/6] Adapter Tests"
	$(PYTHON) -m pytest charm/test/adapters/ -v
	@echo ""
	@echo ">>> [5/6] Benchmark Tests"
	$(PYTHON) -m pytest charm/test/benchmark/ -v
	@echo ""
	@echo ">>> [6/6] Doctest Tests"
	$(PYTHON) -m pytest --doctest-modules charm/zkp_compiler/ --ignore=charm/zkp_compiler/zkp_generator.py --ignore=charm/zkp_compiler/zk_demo.py -v
	@find . -name '*.pyc' -delete
	@echo ""
	@echo "========================================"
	@echo "All test categories complete!"
	@echo "========================================"

.PHONY: test-embed
test-embed:
	@echo "========================================"
	@echo "Running C/C++ Embed API Tests"
	@echo "========================================"
	@echo "Building embed test..."
	@cd embed && $(MAKE) clean
	@cd embed && $(MAKE)
	@echo ""
	@echo "Running embed test..."
ifeq ($(OS),Windows_NT)
	@cd embed && PYTHONPATH=.. ./test.exe
else
	@cd embed && PYTHONPATH=.. ./test
endif
	@echo ""
	@echo "Embed API tests complete."

# Legacy target alias
.PHONY: test-charm
test-charm: test-toolbox

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


