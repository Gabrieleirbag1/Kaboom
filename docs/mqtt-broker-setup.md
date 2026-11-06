# Secure MQTT broker setup (live typing)

Kaboom uses an MQTT broker to show the letters a player types, live, to the other players of the game. The broker is optional: without it the game works, only the live typing is off.

This guide sets up Mosquitto 2 so that:
- players never get a permanent password: the Kaboom server logs in as an admin and gives each player a temporary account that only works for their own game, then deletes it when they leave;
- players connect with TLS (port 8883), so passwords and text can't be read on the network;
- nobody can connect without an account, and an account can't read or write another game.

It assumes a Debian/Ubuntu machine with Mosquitto installed with apt, and the Kaboom server on the same machine (for example with `server_docker.sh`). For a Kaboom server on another machine, see [Kaboom server on another machine](#kaboom-server-on-another-machine).

## 0. Set your domain

Players connect to the broker by a domain name with a valid certificate. Set it once in your shell; the commands below use it:

```sh
DOMAIN=mqtt.example.com          # your domain, pointing to this machine
```

## 1. Install Mosquitto

```sh
sudo apt install mosquitto mosquitto-clients certbot
mosquitto -h | head -1                                       # must be 2.x
PLUGIN=$(dpkg -L mosquitto | grep mosquitto_dynamic_security.so)
echo "$PLUGIN"                                               # must print a path
```

## 2. Admin account

The Kaboom server uses this account to create and delete the players' accounts. Keep its password secret (a password manager); it never goes in a file of the repository.

```sh
openssl rand -base64 24                                      # a strong admin password
sudo mosquitto_ctrl dynsec init /var/lib/mosquitto/dynamic-security.json kaboom-admin
sudo chown mosquitto:mosquitto /var/lib/mosquitto/dynamic-security.json
sudo chmod 600 /var/lib/mosquitto/dynamic-security.json
```

## 3. TLS certificate

Get a Let's Encrypt certificate:

```sh
sudo certbot certonly --standalone -d "$DOMAIN"              # needs port 80 free; else use --webroot or --nginx
sudo ls /etc/letsencrypt/live/                               # the folder name, usually $DOMAIN
```

Mosquitto can't read `/etc/letsencrypt`, so a deploy hook copies the certificate for it after each renewal. Create it (the folder name in it must match the `ls` above):

```sh
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy
sudo tee /etc/letsencrypt/renewal-hooks/deploy/mosquitto.sh > /dev/null <<EOF
#!/bin/sh
install -d -o mosquitto -g mosquitto -m 750 /etc/mosquitto/certs
install -o mosquitto -g mosquitto -m 640 /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/mosquitto/certs/fullchain.pem
install -o mosquitto -g mosquitto -m 600 /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/mosquitto/certs/privkey.pem
systemctl reload mosquitto || true
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/mosquitto.sh
sudo /etc/letsencrypt/renewal-hooks/deploy/mosquitto.sh      # copy it once now
sudo ls -l /etc/mosquitto/certs/                             # fullchain.pem and privkey.pem, owned by mosquitto
sudo certbot renew --dry-run                                 # checks that renewal works
```

## 4. Mosquitto config

Remove anything that defines another way in, so only the file below does: `password_file`, `acl_file`, `listener`, `port` and `allow_anonymous` lines in `/etc/mosquitto/mosquitto.conf` and `/etc/mosquitto/conf.d/*`. Delete the old password and ACL files too: this removes any old shared account.

```sh
grep -rnE "password_file|acl_file|listener|^port|allow_anonymous" /etc/mosquitto/
```

Then create `/etc/mosquitto/conf.d/kaboom.conf`:

```sh
sudo tee /etc/mosquitto/conf.d/kaboom.conf > /dev/null <<EOF
per_listener_settings false
allow_anonymous false
plugin $PLUGIN
plugin_opt_config_file /var/lib/mosquitto/dynamic-security.json

# Messages are tiny; nothing is kept for later subscribers
max_packet_size 2048
retain_available false

# The Kaboom server (same machine), not reachable from the internet
listener 1883 127.0.0.1

# Players: encrypted only
listener 8883
certfile /etc/mosquitto/certs/fullchain.pem
keyfile /etc/mosquitto/certs/privkey.pem
max_connections 3000
EOF
sudo systemctl restart mosquitto
sudo journalctl -u mosquitto -n 30                           # no errors, both listeners open
```

## 5. Deny by default

Without this, a player account could subscribe to `#` and read every game.

```sh
read -s PW                                                   # type the admin password
for t in publishClientSend publishClientReceive subscribe; do
  mosquitto_ctrl -h 127.0.0.1 -u kaboom-admin -P "$PW" dynsec setDefaultACLAccess $t deny
done
mosquitto_ctrl -h 127.0.0.1 -u kaboom-admin -P "$PW" dynsec getDefaultACLAccess
```

## 6. Firewall

Open the players' port only. Port 1883 only listens on 127.0.0.1, but close it in the firewall as well.

```sh
sudo ufw allow 8883/tcp
sudo ufw delete allow 1883/tcp                               # if such a rule exists
```

## 7. Kaboom server

In `Server/confs/mqtt.csv`, set the address the players use:

```
admin_host,127.0.0.1
admin_port,1883
admin_tls,False
player_host,mqtt.example.com
player_port,8883
player_tls,True
```

Give the admin password to the server in a `.env` file next to `server_docker.sh` (`.env` is ignored by git):

```sh
echo "KABOOM_MQTT_PASSWORD=<admin password>" > .env && chmod 600 .env
./server_docker.sh -r
grep MQTT Server/logs/infos.log | tail                       # "Connected to the broker as admin"
```

`server_docker.sh` runs the container with `--network host`, so it reaches the broker on the host's `127.0.0.1:1883`. Without Docker, export `KABOOM_MQTT_PASSWORD` before starting the server. The admin user name is `kaboom-admin` unless `KABOOM_MQTT_USER` says otherwise.

## 8. Check

From another machine:

```sh
mosquitto_sub -h mqtt.example.com -p 1883 -t '#'                                # must fail (port closed)
mosquitto_sub -h mqtt.example.com -p 8883 --capath /etc/ssl/certs -t '#'        # must be refused (no account)
```

Then play a game with two clients: the letters typed by one show up on the other's screen.

## Kaboom server on another machine

The admin then connects over the internet, so it must use TLS too. Skip the `listener 1883 127.0.0.1` part if nothing local uses it, and in `Server/confs/mqtt.csv` set:

```
admin_host,mqtt.example.com
admin_port,8883
admin_tls,True
```

## Upkeep

- **Certificate:** the renewal hook must keep working. If it breaks, live typing stops for everyone when the certificate expires (the game itself keeps working). `sudo certbot renew --dry-run` checks it.
- **`dynamic-security.json`:** the broker rewrites it all the time. It lives on the host disk (`/var/lib/mosquitto`), so it survives restarts. Accounts left by a Kaboom server crash are deleted when the server starts again.
- **Admin password:** if it leaks, change it with `mosquitto_ctrl ... dynsec setClientPassword kaboom-admin`, then update `.env` and restart the Kaboom server.
