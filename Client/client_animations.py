from client_utils import *

class LoadSprites():
    def __init__(self, clientObject):
        self.clientObject = clientObject
        self.setup(clientObject)

    def setup(self, clientObject):
        sprite_folders : list[str] = self.get_sprite_dirs()

        for sprite_dir_name in sprite_folders:
            sprite_files : list[str] = self.setup_sprite_files(sprite_dir_name)
            setattr(clientObject, f"{sprite_dir_name}_sprites", [])
            self.load_sprites(sprite_files, sprite_dir_name)

    def get_sprite_dirs(self) -> list[str]:
        sprite_folders = []
        for root, dirs, files in os.walk(f"{image_path}sprites"):
            for dir in dirs:
                sprite_folders.append(dir)
        print(sprite_folders) 
        return sprite_folders
    
    def setup_sprite_files(self, sprite_dir_name : str) -> list[str]:
        sprite_files = []
        for i in range(32):
            if i < 9:
                sprite_files.append(f"/{sprite_dir_name}/{sprite_dir_name}000{i+1}.png")
            else:
                sprite_files.append(f"/{sprite_dir_name}/{sprite_dir_name}00{i+1}.png")
        return sprite_files

    def load_sprites(self, sprite_files, sprite_dir_name):
        sprites = getattr(self.clientObject, f"{sprite_dir_name}_sprites",)
        for filename in sprite_files:
            pixmap_path = f"{image_path}sprites{filename}"
            pixmap = QPixmap(pixmap_path)
            if pixmap.isNull():
                print(f"Failed to load pixmap from: {pixmap_path}")
            else:
                sprites.append(pixmap)

class AnimatedLabel(QLabel):
    def __init__(self, parent=None):
        super(AnimatedLabel, self).__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.pixmap_name : str | None = None

    def setup(self, parent : object, pixmap_name : str):
        self.pixmap_name = pixmap_name
        try:
            self.sprites : list[QPixmap] = getattr(parent, f"{pixmap_name}_sprites")
        except AttributeError: #temporaire
            self.sprites : list[QPixmap] = getattr(parent, "cactus_sprites")
        self.current_sprite : int = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.pixmap_name == "no-avatar":
            if not self.is_animating():
                self.start_animation()

    def start_animation(self):
        if not self.sprites:
            return
        self.timer.start(1000 // 32)  # 32 frames per second

    def next_frame(self):
        pixmap = self.sprites[self.current_sprite]
        scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(scaled_pixmap)
        self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
        if self.current_sprite == 0:
            self.timer.stop()

    def stop_animation(self):
        self.timer.stop()
        self.current_sprite = 0

    def is_animating(self):
        return self.timer.isActive()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # window = QWidget()
    # window.resize(500, 500)

    # label = AnimatedLabel(window)
    # label.setStyleSheet("background-color: lightgray;")
    # label.setGeometry(0, 0, 500, 500)

    # window.show()

    load_label = LoadSprites(LoadSprites)

    sys.exit(app.exec_())