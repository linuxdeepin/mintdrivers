#!/usr/bin/env python3

from gi.repository import Gtk
import notify2
import sys
import subprocess
import os
from UbuntuDrivers import detect
import apt
import gettext

def get_parent_dir(filepath, level=1):
    parent_dir = os.path.realpath(filepath)
    while(level > 0):
        parent_dir = os.path.dirname(parent_dir)
        level -= 1
    return parent_dir

domain_name = "driver-notifier"
LOCALE_DIR = os.path.join(get_parent_dir(__file__, 2), "po", "mo")
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR="/usr/share/locale"

_ = None
try:
    _ = gettext.translation(domain_name, LOCALE_DIR).gettext
except Exception as e:
    _ = lambda i : i

OVERRIDE_NO_ACTIONS = True
icon = "driver-manager"

def show_cb(n, action):
    assert action == "show"
    subprocess.call("mintdrivers")
    n.close()
    Gtk.main_quit()

def ignore_cb(n, action):
    assert action == "ignore"
    print ("You clicked Ignore")
    n.close()
    Gtk.main_quit()

def close_cb(n):
    Gtk.main_quit()

def showdrivers():
    apt_cache = apt.Cache()
    devices = detect.system_device_drivers()
    nonfree_drivers = 0
    for device in devices:
        for pkg_name in devices[device]['drivers']:
            if not apt_cache[pkg_name].is_installed:
                nonfree_drivers += 1

    if nonfree_drivers > 0:
        return True
    else:
        return False

if not showdrivers():
    sys.exit(1)
if __name__ == '__main__':
    if not notify2.init("Driver Notification", mainloop='glib'):
        sys.exit(1)

    n = notify2.Notification(_("Driver Manager"),
                              _("Find new driver"), icon)
    n.set_urgency(notify2.URGENCY_CRITICAL)
    n.set_category("driver")
    n.add_action("show", _("Install"), show_cb)
    #n.add_action("ignore", "Ignore", ignore_cb)
    n.connect('closed', close_cb)

    if not n.show():
        print ("Failed to send notification")
        sys.exit(1)

    Gtk.main()
