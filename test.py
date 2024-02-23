from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtWidgets import *
import sys, os

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Video Player") 
 
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()
 
        widget = QWidget(self)
        self.setCentralWidget(widget)
 
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
 
        widget.setLayout(layout)
        self.mediaPlayer.setVideoOutput(videoWidget)
 
        self.openFileAutomatically()
 
    def openFileAutomatically(self):
        videoPath = os.path.join(os.path.dirname(__file__), "video/ps2_anim.mp4")
        if os.path.exists(videoPath):
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
            self.mediaPlayer.play()
 
 
app = QApplication(sys.argv)
videoplayer = VideoPlayer()
videoplayer.resize(640, 480)
videoplayer.show()
sys.exit(app.exec_())