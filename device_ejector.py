import re
import subprocess
import time
from warnings import simplefilter

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceEjector:
    def __init__(self):
        simplefilter("ignore")
        self.devices = []
        devices = self.find_devices()
        self.create_main_window(devices)

    def create_main_window(self, devices):
        window = Gtk.Window(title="Device Ejector")
        window.set_default_size(300, 300)
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        # center the grid
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)
        window.add(grid)
        self.add_devices_buttons(grid)
        window.show()
        window.connect("destroy", Gtk.main_quit)
        Gtk.main()

    def find_devices(self):
        user = subprocess.check_output(["whoami"]).decode("utf-8").strip()
        for device in subprocess.check_output(["df"], shell=True).decode("utf-8").split("\n"):
            if "dev/sd" in device:
                device_path = re.search("/dev/sd[a-z]*", device)
                # device_name = re.search(f"/run/media/{user}/", device)
                # device_name = re.search(f"/run/media/{user}/[a-zA-Z0-9_]*", device)
                device_name = device.split(f"/run/media/{user}/")[1]
                self.devices.append([device_name, device_path.group(0)])

        return self.devices

    @staticmethod
    def eject_device(button, device):
        subprocess.call(f"umount {device}*", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        # call udisks command and ignore its output
        subprocess.call(["udisks", "--detach", device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        button.destroy()

    def add_devices_buttons(self, window):
        for device in self.devices:
            button = Gtk.Button(device[0])
            button.connect("clicked", self.eject_device, device[1])

            button.show()
            window.add(button)
        window.show_all()


if __name__ == "__main__":
    DeviceEjector()
