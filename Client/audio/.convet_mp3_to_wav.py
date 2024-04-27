import os
from pydub import AudioSegment

# specify the directory you want to convert
directory = os.path.dirname(os.path.abspath(__file__))

for filename in os.listdir(directory):
    if filename.endswith(".mp3"):
        mp3_sound = AudioSegment.from_mp3(os.path.join(directory, filename))
        # change the extension to .wav
        filename = filename[:-4] + '.wav'
        mp3_sound.export(os.path.join(directory, filename), format="wav")