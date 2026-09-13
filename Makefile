PREFIX ?= /usr/local
DESTDIR ?=
APPDIR = $(DESTDIR)$(PREFIX)/lib/mechrevo-osd-linux
SOURCES = mechrevo_osd.py events.py display.py Overlay.qml LayerOverlay.qml
DRIVER_SOURCES = mechrevo-osd-wmi.c Makefile dkms.conf

.PHONY: install uninstall test
install:
	@test "$(PREFIX)" = /usr/local || { echo 'Service paths require PREFIX=/usr/local'; exit 1; }
	install -d "$(APPDIR)/assets" "$(DESTDIR)/usr/src/mechrevo-osd-0.1.0"
	install -m 644 $(SOURCES) "$(APPDIR)/"
	install -m 644 assets/*.png "$(APPDIR)/assets/"
	install -m 644 packaging/bind-events.py "$(APPDIR)/"
	install -m 644 $(addprefix driver/,$(DRIVER_SOURCES)) "$(DESTDIR)/usr/src/mechrevo-osd-0.1.0/"
	install -Dm 755 packaging/mechrevo-osd "$(DESTDIR)$(PREFIX)/bin/mechrevo-osd"
	install -Dm 644 packaging/70-mechrevo-osd.rules "$(DESTDIR)/etc/udev/rules.d/70-mechrevo-osd.rules"
	install -Dm 644 packaging/mechrevo-osd-binding.service "$(DESTDIR)/etc/systemd/system/mechrevo-osd-binding.service"
	install -Dm 644 packaging/mechrevo-osd.service "$(DESTDIR)$(PREFIX)/share/mechrevo-osd/mechrevo-osd.service"
	install -Dm 644 packaging/mechrevo-osd.desktop "$(DESTDIR)$(PREFIX)/share/applications/mechrevo-osd.desktop"
	install -Dm 644 LICENSE "$(DESTDIR)$(PREFIX)/share/licenses/mechrevo-osd/LICENSE"
	install -m 644 NOTICE "$(DESTDIR)$(PREFIX)/share/licenses/mechrevo-osd/NOTICE"

# Stop the services and remove the DKMS registration first (see README).
uninstall:
	rm -f $(addprefix "$(APPDIR)/,$(addsuffix ",$(SOURCES))) "$(APPDIR)/bind-events.py"
	rm -f $(foreach file,$(notdir $(wildcard assets/*.png)),"$(APPDIR)/assets/$(file)")
	rm -f $(foreach file,$(DRIVER_SOURCES),"$(DESTDIR)/usr/src/mechrevo-osd-0.1.0/$(file)")
	rm -f "$(DESTDIR)$(PREFIX)/bin/mechrevo-osd" "$(DESTDIR)/etc/udev/rules.d/70-mechrevo-osd.rules"
	rm -f "$(DESTDIR)/etc/systemd/system/mechrevo-osd-binding.service"
	rm -f "$(DESTDIR)$(PREFIX)/share/mechrevo-osd/mechrevo-osd.service" "$(DESTDIR)$(PREFIX)/share/applications/mechrevo-osd.desktop"
	rm -f "$(DESTDIR)$(PREFIX)/share/licenses/mechrevo-osd/LICENSE" "$(DESTDIR)$(PREFIX)/share/licenses/mechrevo-osd/NOTICE"

test:
	python3 -m unittest discover -s tests -v
