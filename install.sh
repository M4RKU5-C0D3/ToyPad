#!/usr/bin/env bash
CPD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo apt-get -qqy update
sudo apt-get -qqy install python3-pip python-usb

pip3 install pyusb numpy

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0e6f", ATTR{idProduct}=="0241", MODE="0666"' | sudo tee /etc/udev/rules.d/99-dimensions.rules

export CPD
cat ${CPD}/toypad.service.dist | envsubst | tee ${CPD}/toypad.service
mkdir -p $HOME/.config/systemd/user
ln -sf $CPD/toypad.service $HOME/.config/systemd/user/toypad.service
systemctl --user enable toypad.service
systemctl --user start  toypad.service
systemctl --user status toypad.service
