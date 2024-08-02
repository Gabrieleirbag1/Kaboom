import os

folder_path = '/home/frigiel/Documents/VSCODE/Kaboom/Client/images/sprites/pizza/'

for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
        new_filename = filename.replace('pizouille', 'pizza')
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))