DISTRO_NAME := $(shell lsb_release -sc | tr A-Z a-z)

all:

install:
	mkdir -p $(DESTDIR)usr/sbin
	mkdir -p $(DESTDIR)etc/mcp
	install -m 755 sbin/nullunitIterate $(DESTDIR)usr/sbin
	install -m 755 sbin/nullunitInterface $(DESTDIR)usr/sbin
	install -m 755 sbin/nullunitMasterSync $(DESTDIR)usr/sbin
	install -m 755 sbin/nullunitAddPackageFile $(DESTDIR)usr/sbin

clean:
	rm -fr build

full-clean: clean
	if [ -d debian ] ; then dh_clean; fi
	if [ -d debian ] ; then rm -fr debian; fi

test-distros:
	@echo precise trusty

test-requires:
ifeq (precise, $(DISTRO_NAME))
	@echo python-py
else
	@echo python-pytest
endif

test:
	cd tests && py.test -x iterate.py

lint-requires:
ifeq (trusty, $(DISTRO_NAME))
	@echo linter
endif

lint:
ifeq (trusty, $(DISTRO_NAME))
	linter -i sbin/nullunitMasterSync -i sbin/nullunitInterface
endif

dpkg-distros:
	@echo precise trusty

dpkg-requires:
	@echo dpkg-dev debhelper cdbs

dpkg: full-clean
	./debian-setup
	dpkg-buildpackage -b -us -uc > /tmp/dpkg-build.log

dpkg-file:
	@echo $(shell ls ../nullunit_*.deb)

.PHONY: all clean full-clean test-distros test-requires test lint-requires lint dpkg-distros dpkg-requires dpkg dpkg-file
