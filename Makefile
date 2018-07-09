DISTRO := $(shell lsb_release -si | tr A-Z a-z)
DISTRO_MAJOR_VERSION := $(shell lsb_release -sr | cut -d. -f1)
DISTRO_NAME := $(shell lsb_release -sc | tr A-Z a-z)

all:
	./setup.py build

install:
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/etc/mcp
	mkdir -p $(DESTDIR)/var/lib/config-curator/templates/nullunit/
	install -m 755 bin/nullunitIterate $(DESTDIR)/usr/bin
	install -m 755 bin/nullunitInterface $(DESTDIR)/usr/bin
	install -m 755 bin/nullunitAddPackageFile $(DESTDIR)/usr/bin
	install -m 644 templates/nullunit/* $(DESTDIR)/var/lib/config-curator/templates/nullunit/

	./setup.py install --root $(DESTDIR) --install-purelib=/usr/lib/python3/dist-packages/ --prefix=/usr --no-compile -O0

clean:
	./setup.py clean
	$(RM) -fr build
	$(RM) -f dpkg
	$(RM) -f rpm

full-clean: clean
	$(RM) -fr debian
	$(RM) -fr rpmbuild
	$(RM) -f dpkg-setup
	$(RM) -f rpm-setup

test-distros:
	echo ubuntu-xenial

test-requires:
	echo python-cinp
ifeq (centos, $(DISTRO))
	echo pytest
else ifeq (precise, $(DISTRO_NAME))
	echo python-py
else
	echo python-pytest
endif

test:
	cd tests && py.test -x iterate.py

lint-requires:
ifeq (trusty, $(DISTRO_NAME))
	echo linter
endif

lint:
ifeq (trusty, $(DISTRO_NAME))
	linter
endif

dpkg-distros:
	echo ubuntu-xenial

dpkg-requires:
	echo dpkg-dev debhelper python3-support

dpkg-setup:
	./debian-setup
	touch dpkg-setup

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	echo $(shell ls ../nullunit_*.deb)

rpm-distros:
	#echo centos6

rpm-requires:
	echo rpm-build

rpm-setup:
	./rpmbuild-setup
	touch rpm-setup

rpm:
	rpmbuild -v -bb rpmbuild/config.spec
	touch rpm

rpm-file:
	echo $(shell ls rpmbuild/RPMS/*/nullunit-*.rpm)

.PHONY: all clean full-clean test-distros test-requires test lint-requires lint dpkg-distros dpkg-requires dpkg-file rpm-distros rpm-requires rpm-file
