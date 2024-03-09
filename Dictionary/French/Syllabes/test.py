import csv

def convert_txt_to_csv(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.read()
        words = lines.split(",")  # Séparer les mots par une virgule

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)

        # Parcourir chaque mot et l'écrire dans la colonne correspondante
        for word in words:
            length = len(word)
            row = [''] * (length - 1)  # Créer une liste vide avec la taille correspondant à la longueur du mot
            row.append(word)  # Ajouter le mot à la fin de la liste
            writer.writerow(row)

# Utilisation de la fonction de conversion
input_file = '/home/frigiel/Documents/VSCODE/Kaboom/Server/syllabes.txt'
output_file = '/home/frigiel/Documents/VSCODE/Kaboom/Server/syllabes.csv'
convert_txt_to_csv(input_file, output_file)


def read_words_from_file(input_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
        words = [line.strip().replace(',', '') for line in lines]  # Supprimer les caractères d'espacement comme les sauts de ligne
    
    return words

print(read_words_from_file(output_file))
