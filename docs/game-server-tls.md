# Encrypted game connections (TLS)

The game connection (port 22222) carries the player names, the game passwords and the key that lets a player get their seat back after a disconnection. With TLS it is encrypted, and the game checks that it talks to the real server, not to someone in the middle.

- **The server** loads a certificate (Let's Encrypt), and loads it again by itself when it is renewed: no restart needed.
- **The game** only accepts a certificate issued by a known authority for the server's name (the `host` of its `socket.csv`).

It assumes a Debian/Ubuntu machine and the Kaboom server started with `server_docker.sh`. If you also run the MQTT broker, you already have the certificate: skip to step 2.

## 0. Set your domain and Kaboom folder

```sh
DOMAIN=kaboom.example.com      # the name players connect to, pointing to this machine
KABOOM_DIR=$HOME/Kaboom        # the folder with server_docker.sh
```

## 1. Get a certificate

```sh
sudo apt install certbot
sudo certbot certonly --standalone -d "$DOMAIN"   # needs port 80 free; else use --webroot or --nginx
sudo ls /etc/letsencrypt/live/                    # the folder name, usually $DOMAIN
```

## 2. Copy it for the Kaboom server

The server reads `Server/certs/fullchain.pem` and `Server/certs/privkey.pem` (the `Server` folder is mounted in the container). A certbot deploy hook copies them there now and after each renewal:

```sh
OWNER=$(stat -c %U "$KABOOM_DIR")
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy
sudo tee /etc/letsencrypt/renewal-hooks/deploy/kaboom.sh > /dev/null <<EOF
#!/bin/sh
# Copies the renewed certificate for the Kaboom game server (it loads it again by itself)
install -d -o $OWNER -m 700 $KABOOM_DIR/Server/certs
install -o $OWNER -m 644 /etc/letsencrypt/live/$DOMAIN/fullchain.pem $KABOOM_DIR/Server/certs/fullchain.pem
install -o $OWNER -m 600 /etc/letsencrypt/live/$DOMAIN/privkey.pem $KABOOM_DIR/Server/certs/privkey.pem
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/kaboom.sh
sudo /etc/letsencrypt/renewal-hooks/deploy/kaboom.sh       # copy it once now
ls -l "$KABOOM_DIR/Server/certs/"                          # fullchain.pem and privkey.pem
sudo certbot renew --dry-run                               # checks that renewal works
```

`Server/certs/` is ignored by git: the private key never goes in the repository.

## 3. Turn it on

`Server/confs/socket.csv`:

```
host,0.0.0.0
port,22222
tls,True
certfile,certs/fullchain.pem
keyfile,certs/privkey.pem
```

Paths are relative to the `Server` folder (or absolute). Then restart the server and check its log:

```sh
cd "$KABOOM_DIR"
./server_docker.sh -r
grep TLS Server/logs/infos.log | tail -3      # "Certificate loaded: ..."
```

If the certificate can't be loaded, the server doesn't start, and says why in `Server/logs/errors.log` and `docker logs kaboom-server`.

## 4. The game

The game's `confs/socket.csv` has the server's name, which must be the certificate's name:

```
host,kaboom.example.com
port,22222
tls,True
```

`tls` is on when the line is missing. Players keep their own copy of this file (`~/.config/kaboom/confs/socket.csv` on Linux, `%APPDATA%\Kaboom\confs\socket.csv` on Windows).

Encrypted and plain connections don't understand each other: release the new server and the new game at the same time.

## 5. Check

From another machine:

```sh
openssl s_client -connect kaboom.example.com:22222 -servername kaboom.example.com </dev/null 2>/dev/null \
  | grep -E "subject=|Verify return code"     # CN = your domain, "0 (ok)"
```

Then log in with the game. If it can't connect, its log says why (`~/.config/kaboom/logs/infos.log`):
- `The server's certificate is not valid: ...`: wrong name in `socket.csv`, or an expired certificate;
- `Connection failed (SSLError ...)`: the server doesn't use TLS (`tls,False` on one side only).

## Running locally without a certificate

For a server on your own machine, set `tls,False` in both files: `Server/confs/socket.csv` and the game's `socket.csv` (`~/.config/kaboom/confs/socket.csv`). The server then logs that connections are NOT encrypted. Don't do this on a public server.

## Upkeep

- **Renewal:** certbot renews about a month before expiry and the hook copies the files; new connections use the new certificate, players already connected keep theirs. `sudo certbot renew --dry-run` checks it.
- **If the hook breaks**, players can't connect once the certificate expires (the game says "Connection failed"). Check the date with `openssl x509 -enddate -noout -in Server/certs/fullchain.pem`.
