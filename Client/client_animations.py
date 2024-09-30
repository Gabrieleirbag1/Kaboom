from client_utils import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

class LoadSprites():
    """Class to load all the sprites from the sprites folder
    
    Attributes:
        clientObject (object): The object that will contain all the sprites"""
    def __init__(self, clientObject: object):
        """Load all the sprites from the sprites folder
        
        Args:
            clientObject (object): The object that will contain all the sprites"""
        self.clientObject = clientObject
        self.setup(clientObject)

    def setup(self, clientObject: object):
        """Load all the sprites from the sprites folder
        
        Args:
            clientObject (object): The object that will contain all the sprites"""
        sprite_folders: list[str] = self.get_sprite_dirs()
        start_time = time.time()
        for sprite_dir_name in sprite_folders:
            num_files = len(os.listdir(f"{image_path}sprites/{sprite_dir_name}"))
            sprite_files: list[str] = self.setup_sprite_files(sprite_dir_name, num_files)
            setattr(clientObject, f"{sprite_dir_name}_sprites", [])
            self.load_sprites(sprite_files, sprite_dir_name)
        infos_logger.log_infos("[PIXMAP]", f"Loaded sprites in {time.time() - start_time} seconds")

    def get_sprite_dirs(self) -> list[str]:
        """Get all the sprite directories
        
        Returns:
            list[str]: A list of sprite directory names"""
        sprite_folders = []
        for root, dirs, files in os.walk(f"{image_path}sprites"):
            for dir in dirs:
                sprite_folders.append(dir)
        return sprite_folders
    
    def setup_sprite_files(self, sprite_dir_name: str, num_files: int) -> list[str]:
        """Setup the sprite files
        
        Args:
            sprite_dir_name (str): The name of the sprite directory
            num_files (int): The number of files in the directory
        
        Returns:
            list[str]: A list of sprite file paths"""
        sprite_files = []
        for i in range(num_files):
            if i < 9:
                sprite_files.append(f"/{sprite_dir_name}/{sprite_dir_name}000{i+1}.png")
            else:
                sprite_files.append(f"/{sprite_dir_name}/{sprite_dir_name}00{i+1}.png")
        return sprite_files

    def load_sprites(self, sprite_files: list[str], sprite_dir_name: str):
        """Load the sprites

        Args:
            sprite_files (list[str]): The list of sprite files
            sprite_dir_name (str): The name of the sprite directory"""
        sprites = getattr(self.clientObject, f"{sprite_dir_name}_sprites",)
        for filename in sprite_files:
            pixmap_path = f"{image_path}sprites{filename}"
            pixmap = QPixmap(pixmap_path, format="png")
            if pixmap.isNull():
                infos_logger.log_infos("[PIXMAP]", f"Failed to load pixmap from: {pixmap_path}")
            else:
                sprites.append(pixmap)

class AnimatedLabel(QLabel):
    """Class to create an animated label

    Attributes:
        run_loop (bool): Whether the animation should run in a loop
        frame_rate (int): The frame rate of the animation
        primary_pixmap_name (str | None): The name of the primary pixmap
        pixmap_name (str | None): The name of the pixmap
        sprites (list[QPixmap]): The list of sprites
        current_sprite (int): The current sprite
        timer (QTimer): The timer
        
    Signals:
        animation_finished (str): Signal to indicate that the animation has finished"""
    animation_finished = pyqtSignal(str)
    def __init__(self, parent: QLabel, frame_rate: int):
        """Initialize the AnimatedLabel class

        Args:
            parent (QLabel): The parent label
            frame_rate (int): The frame rate of the animation"""
        super(AnimatedLabel, self).__init__(parent)
        self.run_loop : bool = False
        self.frame_rate = frame_rate
        self.primary_pixmap_name : str | None = None
        self.pixmap_name : str | None = None
        self.sprites : list[QPixmap] = []
        self.current_sprite : int = 0
        self.timer = QTimer()

    def start_animation(self) -> None:
        """Start the animation
        
        Returns:
            None"""
        if not self.sprites:
            return
        self.timer.start(1000 // self.frame_rate)  # Number of frames per second

    def next_frame(self, ratio: Qt.AspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio):
        """Go to the next frame of the animation
        
        Args:
            ratio (Qt.AspectRatioMode): The aspect ratio mode"""
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

    def is_animating(self) -> bool:
        """Check if the animation is running
        
        Returns:
            bool: True if the animation is running, False otherwise"""
        return self.timer.isActive()
    
class AvatarAnimatedLabel(AnimatedLabel):
    """Class to create an animated label for the avatar
    
    Attributes:
        pixmap_name (str): The name of the pixmap"""
    def __init__(self, parent: object = None, frame_rate: int = 24):
        """Initialize the AvatarAnimatedLabel class
        
        Args:
            parent (object): The parent object
            frame_rate (int): The frame rate of the animation"""
        super(AvatarAnimatedLabel, self).__init__(parent, frame_rate)
        self.timer.timeout.connect(self.next_frame)

    def setup(self, parent: object, pixmap_name: str):
        """Setup the avatar

        Args:
            parent (object): The parent object
            pixmap_name (str): The name of the pixmap"""
        self.pixmap_name = pixmap_name
        try:
            self.sprites : list[QPixmap] = getattr(parent, f"{pixmap_name}_sprites")
        except AttributeError: #temporaire
            self.sprites : list[QPixmap] = getattr(parent, "cactus_sprites")
        self.frame_rate = int(len(self.sprites))
        
    def enterEvent(self, event: QEvent):
        """Event when the mouse enters the label
        
        Args:
            event (QEvent): The event"""
        super().enterEvent(event)
        self.play_animation()
    
    def play_animation(self):
        """Play the animation"""
        if not self.pixmap_name == "no-avatar" and settings.accessibility_data[2][1] == "yes":
            if not self.is_animating():
                self.start_animation()

class LoopAnimatedLabel(AnimatedLabel):
    """Class to create a loop animated label
    
    Attributes:
        running (bool): Whether the animation is running
        ratio (Qt.AspectRatioMode): The aspect ratio mode"""
    def __init__(self, parent: AnimatedLabel = None, frame_rate: int = 24, ratio: Qt.AspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio):
        """Initialize the LoopAnimatedLabel class

        Args:
            parent (AnimatedLabel): The parent label
            frame_rate (int): The frame rate of the animation
            ratio (Qt.AspectRatioMode): The aspect ratio mode"""
        super(LoopAnimatedLabel, self).__init__(parent, frame_rate)
        self.running : bool = False
        self.ratio = ratio
        self.timer.timeout.connect(lambda: self.next_frame(self.ratio))

    def setup(self, parent: object, pixmap_name: str):
        """Setup the loop animated label
        
        Args:
            parent (object): The parent object
            pixmap_name (str): The name of the pixmap"""
        self.pixmap_name = pixmap_name
        self.sprites : list[QPixmap] = getattr(parent, f"{pixmap_name}_sprites")
    
    def start_loop_animation(self):
        """Start the loop animation"""
        self.run_loop = True
        self.start_animation()

    def stop_loop_animation(self):
        """Stop the loop animation"""
        self.run_loop = False
        self.stop_animation()