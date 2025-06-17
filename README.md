# Kaboom 💥

## Table of contents  
1. [Introduction](#introduction)  
2. [Rules](#rules)  
3. [Installation](#install)  
    1. [Binary Package](#binary)
    2. [From Source](#source) 
4. [Run Locally](#runlocally)
    1. [Server](#server)
    2. [Client](#client)
5. [Authors](#authors)  


<a name="introduction"></a>
## Introduction 
🇫🇷 Kaboom est un jeu-vidéo multi-joueur en ligne open-source entièrement développé en python avec PyQT5.

🇬🇧 Kaboom is an open-source online multiplayer video game developed entirely in Python with PyQT5.

![Kaboom Screen](https://github.com/Gabrieleirbag1/Kaboom/blob/main/Kaboom.png)  

<a name="rules"></a>
## Rules
🇫🇷 Trouvez un mot contenant la syllabe affichée à l'écran avant que la bombe explose !
Attention, vous ne connaissez pas le temps imparti !

🇬🇧 Find a word containing the syllable displayed on the screen before the bomb explodes!
Be careful, you don't know the time limit!

<a name="install"></a>
## Installation

<a name="binary"></a>
### Binary package
Download the [kaboom-setup-1.1.exe](https://github.com/Gabrieleirbag1/Kaboom/releases/download/1.1/kaboom-setup-1.1.exe) for windows and [kaboom_1.1_all.deb](https://github.com/Gabrieleirbag1/Kaboom/releases/download/1.1/kaboom_1.1_all.deb) on linux.

#### Install
~~~bash
  sudo dpkg -i kaboom_1.1_all.deb
~~~ 

#### Uninstall
~~~bash
  sudo dpkg -r Kaboom
~~~

*Kaboom has been tested on Ubuntu 22.04, Ubuntu 24.04, Debian 12, Windows 10, Windows 11, Mac OS.*

<a name="source"></a>
### From source  
Clone the project  

~~~bash  
  git clone https://github.com/Gabrieleirbag1/Kaboom
~~~

Go to the game directory  

~~~bash  
  cd Kaboom
~~~

Install dependancies and build package

~~~bash
  #linux
  ./kaboom_install.sh 

  #windows (bat)
  ./kaboom_install.bat

  #windows (ps1)
  ./kaboom_install.ps1
~~~

Run client

~~~bash  
  #linux
  ./Kaboom

  #windows
  ./Kaboom
~~~  
<a name="runlocally"></a>
## Run Locally

Kaboom is hosted 24 hours a day on a dedicated server. However, you can launch the server locally with your own settings.

**⚠️ Caution: If you plan to host the server locally, you'll need to configure your router to open the necessary ports. Usage of Linux is also recommanded, as it simplifies the use of sockets and MQTT.**

<a name="server"></a>
### Move to the Server directory 

~~~bash  
  cd Server/
~~~

To host it on your own server, you can modify the configuration files.

#### Open confs/socket.csv
~~~bash
host,0.0.0.0
port,22222
~~~
Change host address if you want to allow only certain addresses.
Adjust the port value if you need to alter the TCP port which the script will use.

#### Open confs/mqtt.csv
~~~bash
broker,missclick.net
port,1883
topic,test
user,siphano
password,F4llenKingdoms##
~~~
For the MQTT part, you'll need to establish your own MQTT broker. If you skip these steps, MQTT functionality will not be available, but you can still use mine. The MQTT server allows you to see the words people are writing in real time.

<a name="client"></a>
### Move to the Client directory 

~~~bash  
  cd Client/
~~~
#### Open confs/socket.csv before building
~~~bash
server,missclick.net
port,22222
~~~
Change host address to your server address / DNS.
Adjust the port value if you need to alter the TCP port which the script will use.

<a name="authors"></a>
## Authors  
- [@Missclick](https://www.github.com/Gabrieleirbag1) (Developer)  
  E-mail : gabrielgarronedev@gmail.com  
  Discord : missclick.net  
- [@Elise](https://linktr.ee/Jellyfishyu) (Graphic designer) 
