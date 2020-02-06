#!/bin/sh

sudo apt-get upgrade
sudo apt-get update

echo "Installing Kivy Dependencies"

sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install -y pkg-config libgl1-mesa-dev libgles2-mesa-dev
sudo apt-get install -y python-setuptools libgstreamer1.0-dev git-core
sudo apt-get install -y gstreamer1.0-plugins-{bad,base,good,ugly}
sudo apt-get install -y gstreamer1.0-{omx,alsa} python-dev libmtdev-dev
sudo apt-get install -y xclip xsel libjpeg-dev


echo "Installing pip Dependencies"

sudo pip3 install --upgrade --user pip setuptools
sudo pip3 install --upgrade --user Cython==0.29.10 pillow


echo "Installing Kivy"

sudo pip3 install --user kivy


echo "Installing serial python packages"

sudo pip3 install smbus2
sudo pip3 install spidev


echo "Installing other necessary packages"

sudo pip3 install shelve
sudo pip3 install pigpio


echo "Configuring Raspberry Pi"




echo "Installing git and cloning repository"

sudo apt-get install -y git
git clone 'https://github.com/pjh26/LoadBox5.0'


echo "Setting up cron jobs"



