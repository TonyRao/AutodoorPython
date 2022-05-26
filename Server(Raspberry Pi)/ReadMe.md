![alt text](https://cdn.discordapp.com/attachments/803997423772631091/880187905321103380/imageedit_3_4925728531.png)
## Setting up the PI

First [Download](https://www.raspberrypi.com/software/operating-systems/) Raspberry Lite os for 64 bit and follow installation procedures.

Make sure its connected to the internet and has a static ip address (this is important for configuring).

Once installed download python 3 by typing

```
sudo apt update
sudo apt install python3
```

## Setting up AutoDoor

![alt text](https://raspberry-valley.azurewebsites.net/img/Pin-Layout-on-Raspberry-Pi-01.png)

AutoDoor uses GPIO pin 17 (pin 11) and GPIO pin 27 (pin 13)

pin 4 for servo power and pin 6 to gorund the servo
pin 39 to ground led pin

## Installing AutoDoor

drop config.json, AutoDoor2.py, and wsserver.py into `/home/pi/`

run the commands below to download the dependencies
```
sudo pip3 install websockets
sudo pip3 install psutil
```

to run autodoor run 
```
cd 
sudo python3 AutoDoor.py
```

AutoDoor will function but won't allow anyone in unless configured. Mouse clicks still work and can be done by plugging in any mouse.

## Configuing AutoDoor

To configure AutoDoor you need The gui software which is currently confgigured to connect to 192.168.12.5 (change this ip address and recompile if required) and wsserver.py to be running

## Run at startup

Run

`sudo crontab -e`

and add this at the bottom of the file and press `ctrl + x` to exit and save 

```
@reboot python3 /home/pi/AutoDoor2.py
@reboot python3 /home/pi/wsserver.py
```

this will make the autodoor and the websocket server start on boot