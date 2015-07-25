DISTRO_NAME := $(shell lsb_release -sc | tr A-Z a-z)

all:

install:
	mkdir -p $(DESTDIR)usr/sbin
	mkdir -p $(DESTDIR)etc/mcp
	mkdir -p $(DESTDIR)var/lib/plato/templates/nullunit/
	install -m 644 templates/nullunit/* $(DESTDIR)var/lib/plato/templates/nullunit/
	install -m 755 sbin/nullunitIterate $(DESTDIR)usr/sbin
	install -m 755 sbin/nullunitInterface $(DESTDIR)usr/sbin
	install -m 755 sbin/nullunitMasterSync $(DESTDIR)usr/sbin
	install -m 755 sbin/nullunitAddPackageFile $(DESTDIR)usr/sbin

clean:
	$(RM) -fr build

full-clean: clean
	$(RM) -fr debian
	$(RM) -fr rpmbuild

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
	dpkg-buildpackage -b -us -uc > /tmp/dpkg-build.log 2>&1

dpkg-file:
	@echo $(shell ls ../nullunit_*.deb)

rpm-distros:
	@echo centos6

rpm-requires:
	@echo rpm-build

rpm: full-clean
	./rpm-setup
	rpmbuild -v -bb rpmbuild/config.spec > /tmp/rpm-build.log 2>&1

rpm-file:
	@echo $(shell ls rpmbuild/RPMS/noarch/nullunit-*.rpm)

.PHONY: all clean full-clean test-distros test-requires test lint-requires lint dpkg-distros dpkg-requires dpkg dpkg-file rpm-distros rpm-requires rpm rpm-file
