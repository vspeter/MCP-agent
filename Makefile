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

test-targets:
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
	@echo linter

lint:
	linter

dpkg-targets:
	@echo precise trusty

dpkg-requires:
	@echo dpkg-dev

dpkg: full-clean
	./debian-setup
	dpkg-buildpackage -b -us -uc

dpkg-file:
	@echo $(shell ls ../nullunit_*.deb)

.PHONY: all clean full-clean test-targets test-requires test lint-requires lint dpkg-targets dpkg-requires dpkg dpkg-file
