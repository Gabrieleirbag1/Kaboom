from client_utils import *
import log_config

log_config.setup_logging()

class LoadSprites():
    def __init__(self, clientObject):
        self.clientObject = clientObject
        self.setup(clientObject)

    def setup(self, clientObject):
        sprite_folders : list[str] = self.get_sprite_dirs()
        start_time = time.time()
        for sprite_dir_name in sprite_folders:
            num_files = len(os.listdir(f"{image_path}sprites/{sprite_dir_name}"))
            sprite_files : list[str] = self.setup_sprite_files(sprite_dir_name, num_files)
            setattr(clientObject, f"{sprite_dir_name}_sprites", [])
            self.load_sprites(sprite_files, sprite_dir_name)
        print(f"Loaded sprites in {time.time() - start_time} seconds")

    def get_sprite_dirs(self) -> list[str]:
        sprite_folders = []
        for root, dirs, files in os.walk(f"{image_path}sprites"):
            for dir in dirs:
                sprite_folders.append(dir)
        print(sprite_folders) 
        return sprite_folders
    
    def setup_sprite_files(self, sprite_dir_name : str, num_files : int) -> list[str]:
        sprite_files = []
        for i in range(num_files):
            if i < 9:
                sprite_files.append(f"/{sprite_dir_name}/{sprite_dir_name}000{i+1}.png")
            else:
                sprite_files.append(f"/{sprite_dir_name}/{sprite_dir_name}00{i+1}.png")
        return sprite_files

    def load_sprites(self, sprite_files, sprite_dir_name):
        sprites = getattr(self.clientObject, f"{sprite_dir_name}_sprites",)
        for filename in sprite_files:
            pixmap_path = f"{image_path}sprites{filename}"
            pixmap = QPixmap(pixmap_path, format="png")
            if pixmap.isNull():
                print(f"Failed to load pixmap from: {pixmap_path}")
            else:
                sprites.append(pixmap)

class AnimatedLabel(QLabel):
    animation_finished = pyqtSignal(str)
    def __init__(self, parent : QLabel, frame_rate : int):
        super(AnimatedLabel, self).__init__(parent)
        self.run_loop : bool = False
        self.frame_rate = frame_rate
        self.pixmap_name : str | None = None
        self.sprites : list[QPixmap] = []
        self.current_sprite : int = 0
        self.timer = QTimer()

    def start_animation(self):
        if not self.sprites:
            return
        self.timer.start(1000 // self.frame_rate)  # Number of frames per second

    def next_frame(self, ratio=Qt.AspectRatioMode.KeepAspectRatio):
        pixmap = self.sprites[self.current_sprite]
        scaled_pixmap = pixmap.scaled(self.size(), ratio)
        self.setPixmap(scaled_pixmap)
        self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
        if self.current_sprite == 0:
            self.timer.stop()
            if self.run_loop:
                self.start_animation()
            else:
                self.animation_finished.emit(self.pixmap_name)

    def stop_animation(self):
        self.timer.stop()
        self.current_sprite = 0

    def is_animating(self):
        return self.timer.isActive()
    
    def is_ended(self):
        return self.ended
    
class AvatarAnimatedLabel(AnimatedLabel):
    def __init__(self, parent=None, frame_rate=24):
        super(AvatarAnimatedLabel, self).__init__(parent, frame_rate)
        self.timer.timeout.connect(self.next_frame)

    def setup(self, parent : object, pixmap_name : str):
        self.pixmap_name = pixmap_name
        try:
            self.sprites : list[QPixmap] = getattr(parent, f"{pixmap_name}_sprites")
        except AttributeError: #temporaire
            self.sprites : list[QPixmap] = getattr(parent, "cactus_sprites")
        self.frame_rate = int(len(self.sprites))
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self.play_animation()
    
    def play_animation(self):
        if not self.pixmap_name == "no-avatar" and settings.accessibility_data[2][1] == "yes":
            if not self.is_animating():
                self.start_animation()

class LoopAnimatedLabel(AnimatedLabel):
    def __init__(self, parent=None, frame_rate=24, ratio=Qt.AspectRatioMode.KeepAspectRatio):
        super(LoopAnimatedLabel, self).__init__(parent, frame_rate)
        self.running : bool = False
        self.ratio = ratio
        self.timer.timeout.connect(lambda: self.next_frame(self.ratio))

    def setup(self, parent : object, pixmap_name : str):
        self.pixmap_name = pixmap_name
        self.sprites : list[QPixmap] = getattr(parent, f"{pixmap_name}_sprites")
    
    def start_loop_animation(self):
        self.run_loop = True
        self.start_animation()

    def stop_loop_animation(self):
        self.run_loop = False
        self.stop_animation()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    window.resize(500, 500)

    # label = AnimatedLabel(window)
    # label.setStyleSheet("background-color: lightgray;")
    # label.setGeometry(0, 0, 500, 500)

    # window.show()

    load_label = LoadSprites(LoadSprites)
    label = LoopAnimatedLabel()
    label.setup(LoadSprites, "bombe")
    label.start_loop_animation()

    window.show()

    sys.exit(app.exec_())