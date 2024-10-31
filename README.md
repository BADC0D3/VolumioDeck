# VolumioDeck

## Volumio Deck Setup
### Ensure system is up to date, upgrade all out of date packages
``` bash
sudo apt update && sudo apt dist-upgrade -y
```

### Install the pip Python package manager
``` bash
sudo apt install -y python3-pip python3-setuptools
```

### Install system packages needed for the default LibUSB HIDAPI backend
``` bash
sudo apt install -y libudev-dev libusb-1.0-0-dev libhidapi-libusb0
```

### Install system packages needed for the Python Pillow package installation
``` bash
sudo apt install -y libjpeg-dev zlib1g-dev
```

### Install python library dependencies
``` bash
pip3 install wheel
pip3 install pillow
```

### Add udev rule to allow all users non-root access to Elgato StreamDeck devices:
``` bash
sudo tee /etc/udev/rules.d/10-streamdeck.rules << EOF
    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fd9", GROUP="users"
EOF
```

### Install the latest version of the StreamDeck library via pip
``` bash
pip3 install -r requirements
```

### Start VolumeDeck
``` bash
chmod +x run.sh
./run.sh
```

## Volumio Deck Service

### Install Service
``` bash
chmod +x service_install.sh
./service_install.sh
```

### Uninstall Service
``` bash
chmod +x service_uninstall.sh
./service_uninstall.sh
```

## Volumio Deck Controls

![alt text](images/mydeck.jpg "MyDeck")

### Dial 1
    - Turn Clockwise: Increase the deck brightness
    - Turn Counter Clockwise: Decrease the deck brighness
    - Press: Toogle the deck display

### Dial 2
    - Turn Clockwise: Go to the next page of tiles
    - Turn Counter Clockwise: Go to the prev page of tiles
    - Press: Reload tiles from json file

### Dial 3
    - Turn Clockwise: Next Track
    - Turn Counter Clockwise: Prev Tack
    - Press: Toogle Play/Pause

### Dial 4
    - Turn Clockwise: Increase the Volume
    - Turn Counter Clockwise: Decrease the Volume
    - Press: Toogle Mute
