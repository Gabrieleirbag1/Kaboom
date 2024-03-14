import csv, os

def read_words_from_file():
    """read_words_from_file() : Fonction qui permet de lire les mots d'un fichier texte
    
    Args:
        input_file (str): Chemin du fichier texte à lire"""
    chemin_csv = os.path.join(os.path.dirname(__file__), "../Dictionary/French/Syllabes/syllabes.csv")
    with open(chemin_csv, 'r') as file:
        lines = file.readlines()
        words = [line.strip().replace(',', '') for line in lines]  # Supprimer les caractères d'espacement comme les sauts de ligne
    
    return words

def get_csv(chemin_du_fichier_csv):
    """get_csv() : Fonction qui permet de récupérer les données d'un fichier csv
    
    Args:
        chemin_du_fichier_csv (str): Chemin du fichier csv à lire"""
    premiere_colonne = []

    with open(chemin_du_fichier_csv, 'r', newline='', encoding='utf-8') as fichier_csv:
        lecteur_csv = csv.reader(fichier_csv)
        for ligne in lecteur_csv:
            if ligne:  # Vérifier si la ligne n'est pas vide
                premiere_colonne.append(ligne[0])

    return premiere_colonne

# Exemple d'utilisation
chemin_du_fichier_csv = os.path.join(os.path.dirname(__file__), "../Dictionary/French/Dictionary/dictionary.csv")

dictionnaire = get_csv(chemin_du_fichier_csv)
arret = False
looking_for_games_players = [] #socket
conn_list = [] #socket
reception_list = {"Conn": [], "Reception": []} #socket, Reception
game_list = {"Creator": [], "Name": [], "Password": [], "Private": [], "Game_Object": [], "Players_Number": []} #str, str, str, bool, Game, int
game_tour = {"Player": [], "Conn": [], "Ready": [], "InGame": [], "Game": []} #str, socket, bool, bool, str

