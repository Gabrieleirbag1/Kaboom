"""TLS certificate of the game server (#19).

The certificate is renewed every few months (certbot copies the new files over the old ones).
New connections use the new files as soon as they are complete: no restart needed.
"""
import os
import ssl

from server_logs import InfosLogger

infos_logger = InfosLogger()


class ServerTLS:
    def __init__(self, certfile: str, keyfile: str):
        self.certfile, self.keyfile = certfile, keyfile
        self._context: ssl.SSLContext | None = None
        self._loaded: tuple | None = None  # modification times of the files in use
        self.context()  # fails now if the files are missing or wrong

    def context(self) -> ssl.SSLContext:
        """The context for a new connection: the current files, or the last good ones while
        certbot is copying them (a new certificate with the old key fails to load)."""
        try:
            stamp = (os.stat(self.certfile).st_mtime_ns, os.stat(self.keyfile).st_mtime_ns)
        except OSError:
            if self._context is None:
                raise
            return self._context
        if stamp != self._loaded:
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.minimum_version = ssl.TLSVersion.TLSv1_2
                context.load_cert_chain(self.certfile, self.keyfile)
            except (OSError, ssl.SSLError) as e:
                if self._context is None:
                    raise
                infos_logger.log_infos("[TLS]", f"New certificate not loaded yet ({e}), keeping the old one")
                return self._context
            self._context, self._loaded = context, stamp
            infos_logger.log_infos("[TLS]", f"Certificate loaded: {self.certfile}")
        return self._context
