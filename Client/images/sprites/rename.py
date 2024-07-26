import os

folder_path = '/home/frigiel/Documents/VSCODE/Kaboom/Client/images/sprites/title_screen/'

for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
        new_filename = filename.replace('ecran_complet', 'title_screen')
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))