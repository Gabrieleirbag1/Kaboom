import os

folder_path = '/home/frigiel/Documents/VSCODE/Kaboom/Client/images/sprites/gameboy2/'

for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
        new_filename = filename.replace('gb_sx_v_st', 'gameboy')
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))