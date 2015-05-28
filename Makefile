all:

install:
	mkdir -p $(DESTDIR)usr/sbin
	mkdir -p $(DESTDIR)etc/mcp
	install -m 755 sbin/nullunitIterate $(DESTDIR)usr/sbin

clean:
	rm -fr build
	dh_clean

test:
	cd tests && py.test -x iterate.py

lint:

dpkg:
	dpkg-buildpackage -b -us -uc
	dh_clean

dpkg-file:
	echo $(shell ls ../nullunit_*.deb)

.PHONY: all clean test install lint dpkg
