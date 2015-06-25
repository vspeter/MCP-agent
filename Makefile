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
	dh_clean
	rm -fr debian

test:
	cd tests && py.test -x iterate.py

lint:

dpkg: clean
	debian-setup
	dpkg-buildpackage -b -us -uc
	dh_clean

dpkg-file:
	@echo $(shell ls ../nullunit_*.deb)

.PHONY: all clean test lint dpkg dpkg-file
