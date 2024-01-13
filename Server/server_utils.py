import csv, os

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
chemin_du_fichier_csv = os.path.join(os.path.dirname(__file__), "../French-Dictionary/dictionary/dictionary.csv")

dictionnaire = get_csv(chemin_du_fichier_csv)



arret = False
conn_list = []
game_list = []
game_tour = {"Player": [], "Conn": [], "Syllabe": [], "Game": []}
