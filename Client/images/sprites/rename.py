import os

folder_path = '/home/frigiel/Documents/VSCODE/Kaboom/Client/images/sprites/tombe4_'

for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
        new_filename = filename.replace('tombe4', 'tombe4_')
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))