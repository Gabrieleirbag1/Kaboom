import csv, unidecode, re

read_path = '/home/frigiel/Documents/VSCODE/Kaboom/Dictionary/French/Dictionary/dictionary.csv'

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

def check_syllabes_in_words():
    """check_syllabes_in_words() : Fonction qui permet de vérifier si les syllabes sont dans les mots"""
    words = get_csv(read_path)
    syllabes_list = {"Syllabe": [], "Apparition": []}

    for word in words[147:148]:
        for i in range(len(word)):
            print(word)
            try:
                sylb = unidecode.unidecode(f"{word[i]}{word[i+1]}").lower()
                if sylb == re.sub(r'[^a-zA-ZÀ-ÿ]', '', sylb):
                    if sylb not in syllabes_list['Syllabe']:
                        syllabes_list['Syllabe'].append(sylb)

                    index_sylb = syllabes_list['Syllabe'].index(sylb)

                    try:
                        syllabes_list['Apparition'][index_sylb] = syllabes_list['Apparition'][index_sylb] + 1
                    except IndexError:
                        syllabes_list['Apparition'].append(1)

            except IndexError:
                continue
    

    return syllabes_list

print(check_syllabes_in_words()["Syllabe"])

            

