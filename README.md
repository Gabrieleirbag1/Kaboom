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
Kaboom comes fully compiled: Python and Qt are inside, there is nothing else to install.

Download the [kaboom-setup-1.2.exe](https://github.com/Gabrieleirbag1/Kaboom/releases/download/1.2/kaboom-setup-1.2.exe) for windows and [kaboom_1.2_amd64.deb](https://github.com/Gabrieleirbag1/Kaboom/releases/download/1.2/kaboom_1.2_amd64.deb) on linux. Kaboom is also available on Steam (Windows and Linux).

#### Install
~~~bash
  sudo apt install ./kaboom_1.2_amd64.deb
~~~ 

#### Uninstall
~~~bash
  sudo apt remove kaboom
~~~

*Kaboom has been tested on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 26.04, Debian 12, Windows 10, Windows 11, Mac OS.*

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

Build the compiled game (needs Python 3.14). The scripts make a virtual environment, install
`requirements-build.txt` and run `build.py`.

~~~bash
  #linux (--desktop also adds Kaboom to your applications menu)
  ./kaboom_install.sh

  #windows (bat)
  ./kaboom_install.bat

  #windows (ps1)
  ./kaboom_install.ps1
~~~

Add `--package` to also make the installer (`Releases/kaboom_<version>_amd64.deb`, or
`Releases/kaboom-setup-<version>.exe` with [Inno Setup 6](https://jrsoftware.org/isdl.php)), and
`--smoke` to check the built game starts. Releases and Steam uploads: see [docs/release.md](docs/release.md).

Run client

~~~bash  
  #linux
  ./dist/linux/Kaboom/Kaboom

  #windows
  ./dist/windows/Kaboom/Kaboom.exe
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
tls,True
certfile,certs/fullchain.pem
keyfile,certs/privkey.pem
~~~
Change host address if you want to allow only certain addresses.
Adjust the port value if you need to alter the TCP port which the script will use.

The game connections are encrypted (TLS) with a certificate for your domain: follow the [game server TLS guide](docs/game-server-tls.md). Without a certificate the server doesn't start; to run it locally without one, set `tls,False` here and in the client's `socket.csv`.

#### Open confs/mqtt.csv
~~~bash
admin_host,127.0.0.1
admin_port,1883
admin_tls,False
player_host,missclick.net
player_port,8883
player_tls,True
~~~
The MQTT broker shows the words people are typing in real time. It is optional: without it the game works, only the live typing is off.

It needs Mosquitto 2 with the dynamic security plugin. The server logs into the broker as an admin (`admin_*`) and gives each player a temporary account that only works for their game (`player_*` is the address the players use). The admin password is never in a file of the repository: set it in the environment, for example in a `.env` file next to `server_docker.sh`:
~~~bash
KABOOM_MQTT_PASSWORD=your-admin-password
~~~
To set up a secured broker (TLS, one temporary account per player), follow the [MQTT broker setup guide](docs/mqtt-broker-setup.md).

<a name="client"></a>
### Move to the Client directory 

~~~bash  
  cd Client/
~~~
#### Open confs/socket.csv before building
~~~bash
host,missclick.net
port,22222
tls,True
~~~
Change host address to your server address / DNS: it must be the name on the server's certificate.
Adjust the port value if you need to alter the TCP port which the script will use.
`tls,False` only for a local server without a certificate (see the [game server TLS guide](docs/game-server-tls.md)).

<a name="authors"></a>
## Authors  
- [@Missclick](https://www.github.com/Gabrieleirbag1) (Developer)  
  E-mail : gabrielgarronedev@gmail.com  
  Discord : missclick.net  
- [@Elise](https://linktr.ee/Jellyfishyu) (Graphic designer) 
