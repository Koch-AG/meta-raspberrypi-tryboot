include recipes-core/images/core-image-base.bb

COMPATIBLE_MACHINE = "^rpi$"

IMAGE_FEATURES += " \
        package-management \
        ssh-server-dropbear \
        ssh-server-openssh \
"

IMAGE_INSTALL += " \
    rpi-eeprom \
    raspi-gpio \
    bcm2835 \
    pi-blaster \
    linux-firmware \
"

