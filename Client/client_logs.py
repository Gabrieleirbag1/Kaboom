import logging, sys, os, traceback
from datetime import datetime

# Create the base path
if sys.platform == "win32":
    base_path = os.path.join(os.getenv('APPDATA'), "Kaboom")
else:
    base_path = os.path.join(os.path.expanduser("~"), ".config", "kaboom")

class ErrorLogger:
    @staticmethod
    def setup_logging():
        """
        Configures the logger to capture errors and uncaught exceptions.
        """
        log_file_path = os.path.join(base_path, 'logs/errors.log')
        
        # Ensure the logs directory exists
        logs_dir = os.path.dirname(log_file_path)
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Ensure the log file exists
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w'):
                pass

        # Configure basic logging
        logging.basicConfig(filename=log_file_path,
                            filemode='a',  # Append to existing file
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.ERROR)

        def handle_exception(exc_type: type, exc_value: Exception, exc_traceback: traceback):
            """
            Handles uncaught exceptions by logging them.

            Args:
                exc_type (type): Exception type.
                exc_value (Exception): Exception instance.
                exc_traceback (traceback): Traceback object.
            """
            logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        # Replace sys.excepthook to log uncaught exceptions
        sys.excepthook = handle_exception

        class StderrLogger(object):
            """Redirects stderr to the logger."""
            def write(self, message: str):
                """
                Writes a message to the logger.

                Args:
                    message (str): The message to log.
                """
                logging.error(message)

            def flush(self):
                """
                Flushes the buffer (no-op).
                """
                pass  # This could be implemented if necessary

        sys.stderr = StderrLogger()

class InfosLogger():
    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        """
        Configures the logger to capture errors and uncaught exceptions.
        """
        log_file_path = os.path.join(base_path, 'logs/infos.log')
        
        # Ensure the logs directory exists
        logs_dir = os.path.dirname(log_file_path)
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Ensure the log file exists
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w'):
                pass

    def log_infos(self, state: str, message: str):
        """
        Logs infos message with the current timestamp.

        Args:
            message (str): The message to log.
        """
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(base_path, 'logs/infos.log'), 'a') as log_file:
            log_file.write(f"{time} - {state} - {message}\n")