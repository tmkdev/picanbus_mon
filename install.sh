#!/bin/bash

cd $HOME

if [ "$USER" != "pi" ]; then
    echo "This script is intended to install to user pi. $USER is not supported."
    exit 2
fi

echo "This script will attempt to install picanbus_mon on your pi. It might actually work."
echo "It does envoke sudo - so I'll wait for 10 secs to make sure your OK with that..."
sleep 10

echo "Updating repo cache"
sudo apt-get update
echo "Updating OS to latest"
sudo apt-get upgrade -y 
echo "Installing git"
sudo apt-get install -y git 

git clone --recurse-submodules https://github.com/tmkdev/picanbus_mon.git

echo "Install packages from picanbus_mon.doc"
cd $HOME/picanbus_mon
sudo apt-get install -y $(cat packages.doc)
echo "Installing cantools from pypi"
sudo pip3 install cantools

echo "Configuring vcan module"
if grep -Fxq "vcan" /etc/modules
then
    echo "Already configured"
else
    sudo echo "vcan" >> /etc/modules
fi

echo "Configuring can interfaces"
sudo cp scripts/can0 /etc/network/interfaces.d/
sudo cp scripts/vcan0 /etc/network/interfaces.d/

echo "Configuring cadillac boot screen"

echo "Swapping boot/config.txt"
if [ ! -f "/boot/config.txt.orig" ]; then
    echo "Backing up config.txt.. "
    sudo cp /boot/config.txt /boot/config.txt.orig
fi 
sudo cp scripts/config.txt /boot/config.txt

# /boot/cmdline.txt needs 
# logo.nologo and consoleblank=0 loglevel=1 quiet appeneded.

echo "Configuring /boot/cmdline.txt"
if grep -Fxq "logo.nologo consoleblank=0 loglevel=1 quiet" /boot/cmdline.txt
then
    echo "Already configured"
else
    sudo sed -i '$s/$/ logo.nologo consoleblank=0 loglevel=1 quiet/' /boot/cmdline.txt
fi

echo "Disabling login prompt at boot"
sudo systemctl disable getty@tty1

echo "Setting up spashscreen service"
sudo cp scripts/splashscreen.service /etc/systemd/system/
sudo systemctl enable splashscreen

echo "Setting root cron"
sudo crontab script/root_boot_crontab

echo "Setting RUNFLAG /home/pi/RUNDISP. If this file exists the pi boots into the display automatically. Delete if that's not what you want."
touch /home/pi/RUNDISP

echo "Done?! Rebooting in 10 seconds"
sleep 10

sudo reboot