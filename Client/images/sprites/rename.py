import os

folder_path = '/home/frigiel/Documents/VSCODE/Kaboom/Client/images/sprites/explosion/'

for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
        new_filename = filename.replace('Chronologie 1_', 'explosion')
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))