import logging, sys, os

def setup_logging():
    """setup_loggin() : Configuration du logger pour capturer les erreurs et les exceptions non gérées"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_dir, 'game_errors.log')

    # Configure basic logging
    logging.basicConfig(filename=log_file_path,
                        filemode='a',  # Ajouter au fichier existant
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.ERROR)

    # Fonction pour gérer les exceptions non gérées
    def handle_exception(exc_type, exc_value, exc_traceback):
        logging.error("Exception non gérée", exc_info=(exc_type, exc_value, exc_traceback))

    # Remplacer sys.excepthook pour enregistrer les exceptions non gérées
    sys.excepthook = handle_exception

    # Optionnel: Rediriger stderr pour capturer les erreurs des bibliothèques externes
    class StderrLogger(object):
        """StderrLogger : Classe qui permet de rediriger stderr vers le logger"""
        def write(self, message):
            """write(message) : Fonction qui permet d'écrire un message dans le logger"""
            logging.error(message)

        def flush(self):
            """flush() : Fonction qui permet de vider le buffer"""
            pass  # Cela pourrait être implémenté si nécessaire

    sys.stderr = StderrLogger()