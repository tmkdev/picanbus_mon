#!/bin/bash
if [ "$USER" != "pi" ]; then
    echo "This script is intended to install to user pi. $USER is not supported."
    exit 2
fi

cd $HOME

echo "This script will attempt to install picanbus_mon on your pi. It might actually work."
echo "It does envoke sudo - so I'll wait for 10 secs to make sure your OK with that..."
sleep 10

echo "Updating repo cache"
sudo apt-get update
echo "Updating OS to latest"
sudo apt-get upgrade -y 
echo "Installing git"
sudo apt-get install -y git 

echo "Cloning picanbus_mon"
git clone --recurse-submodules https://github.com/tmkdev/picanbus_mon.git

cd $HOME/picanbus_mon
echo "Pulling latest if this script is rerun..."
git pull origin master

echo "Install packages from picanbus_mon.doc"
sudo apt-get install -y $(cat packages.doc)
echo "Installing cantools from pypi"
sudo pip3 install cantools

echo "Configuring vcan module"
grep -Fxq "vcan" /etc/modules
vcanset=$?

if [ "$vcanset" -eq 0 ]; 
then
    echo "Already configured"
else
     sudo bash -c "echo vcan >> /etc/modules"
fi

echo "Configuring can interfaces"
sudo cp scripts/can0 /etc/network/interfaces.d/
sudo cp scripts/vcan0 /etc/network/interfaces.d/

echo "Configuring cadillac boot screen"
sudo cp cardisp/images/cadillac-logo.jpg /opt/splash.jpg

echo "Swapping boot/config.txt"
if [ ! -f "/boot/config.txt.orig" ]; then
    echo "Backing up config.txt.. "
    sudo cp /boot/config.txt /boot/config.txt.orig
fi 

echo "Configuring config.txt"
sudo sed -i -r 's/^#?disable_overscan.*$/disable_overscan=0/' /boot/config.txt
sudo sed -i -r 's/^#?overscan_left.*$/overscan_left=0/' /boot/config.txt
sudo sed -i -r 's/^#?overscan_right.*$/overscan_right=0/' /boot/config.txt
sudo sed -i -r 's/^#?overscan_top.*$/overscan_top=0/' /boot/config.txt
sudo sed -i -r 's/^#?overscan_bottom.*$/overscan_bottom=0/' /boot/config.txt
sudo sed -i -r 's/^#?framebuffer_width.*$/framebuffer_width=1280/' /boot/config.txt
sudo sed -i -r 's/^#?framebuffer_height.*$/framebuffer_height=720/' /boot/config.txt
sudo sed -i -r 's/^#?dtparam=i2c_arm.*$/dtparam=i2c_arm=on/' /boot/config.txt
grep -Fxq "sdtv_aspect=3" /boot/config.txt || sudo bash -c "echo 'sdtv_aspect=3' >> /boot/config.txt"
grep -Fxq "dtoverlay=i2c-rtc" /boot/config.txt ||  sudo bash -c "echo 'dtoverlay=i2c-rtc,ds3231' >> /boot/config.txt"

if [ ! -f "/boot/cmdline.txt.orig" ]; then
    echo "Backing up cmdline.txt.. "
    sudo cp /boot/cmdline.txt /boot/cmdline.txt.orig
fi 

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
sudo crontab scripts/root_boot_crontab

echo "Setting RUNFLAG /home/pi/RUNDISP. If this file exists the pi boots into the display automatically. Delete if that's not what you want."
touch /home/pi/RUNDISP

echo "Getting opensource font sekawk for segoeui"
mkdir fonts
wget https://github.com/winjs/winstrap/blob/5a3c1341190e7585fd550e01cfded50ae4e8a4c7/src/fonts/selawk.ttf?raw=true -O fonts/selawk.ttf
cd fonts
ln -s selawk.ttf segoeui.ttf
cd ..

echo "Done?! Rebooting in 10 seconds"
sleep 10

sudo reboot3