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

    for word in words:
        for i in range(len(word)):
            # print(word)
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

def del_syllabes(syllabes_list):
    """del_syllabes() : Fonction qui permet de supprimer les syllabes qui apparaissent moins de x fois"""
    del_list_index = []
    for index, apparition in enumerate(syllabes_list["Apparition"]):
        if apparition < 50:
            del_list_index.append(index)

    print(del_list_index)
    print(len(del_list_index))

    del_list = [syllabes_list["Syllabe"][index] for index in del_list_index]
    for syb in del_list:
        index_syb = syllabes_list["Syllabe"].index(syb)
        syllabes_list["Syllabe"].pop(index_syb)
        syllabes_list["Apparition"].pop(index_syb)

    print("_______________________________\n")
    print(syllabes_list)
    print(len(syllabes_list["Syllabe"]))

if __name__ == "__main__":
    syllabes_list = check_syllabes_in_words()
    # print(syllabes_list["Syllabe"])
    # print(syllabes_list["Apparition"])
    # print(len(syllabes_list['Syllabe']))
    # print(len(syllabes_list['Apparition']))
    del_syllabes(syllabes_list)

