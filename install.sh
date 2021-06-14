#!/usr/bin/env bash
CPD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo apt-get -qqy update
sudo apt-get -qqy install python-usb

pip3 install pyusb

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0e6f", ATTR{idProduct}=="0241", MODE="0666"' | sudo tee /etc/udev/rules.d/99-dimensions.rules
