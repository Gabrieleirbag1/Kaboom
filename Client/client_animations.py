from client_utils import *
from client_logs import ErrorLogger
from client_windows import LoadingWindow

import math
from concurrent.futures import ThreadPoolExecutor

ErrorLogger.setup_logging()


def sprite_size(sprite_dir_name: str) -> QSize:
    """The biggest size a frame of this animation is shown at (frames are kept at that size).

    The title screen fills the screen; the bomb and the explosions fill a third of its height
    (bomb_label); avatars and tombstones a sixth (avatar labels, 1/5.9 for the player whose turn it
    is). Frames are never made bigger than their file.

    Args:
        sprite_dir_name (str): The name of the sprite directory

    Returns:
        QSize: The biggest size the frames are shown at"""
    if sprite_dir_name == "title_screen":
        return QSize(screen_width, screen_height)
    divisor = 3 if sprite_dir_name.startswith(("bombe", "explosion")) else 5.9
    side = math.ceil(min(screen_width, screen_height) / divisor)
    return QSize(side, side)


def read_sprite(path: str, size: QSize, mode: Qt.AspectRatioMode) -> QImage:
    """Read a frame and shrink it to `size`. Runs in a worker thread: QImage, not QPixmap.

    Args:
        path (str): The frame's file
        size (QSize): The biggest size it is shown at
        mode (Qt.AspectRatioMode): KeepAspectRatio, or IgnoreAspectRatio to stretch it like its label

    Returns:
        QImage: The frame (null if it couldn't be read)"""
    image = QImageReader(path).read()
    if image.isNull():
        return image
    target = image.size().scaled(size, mode).boundedTo(image.size())
    if target == image.size():
        return image
    return image.scaled(target, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


class LoadSprites():
    """Class to load all the sprites from the sprites folder
    
    Attributes:
        clientObject (object): The object that will contain all the sprites
        loading_window (LoadingWindow, optional): Loading window with progress bar
    """
    def __init__(self, clientObject: object, loading_window: LoadingWindow = None):
        """Load all the sprites from the sprites folder
        
        Args:
            clientObject (object): The object that will contain all the sprites
            loading_window (LoadingWindow, optional): Loading window to show progress
        """
        self.clientObject = clientObject
        self.loading_window = loading_window
        self.loaded_sprites = 0
        self.setup(clientObject)

    def setup(self, clientObject: object):
        """Load all the sprites from the sprites folder
        
        Args:
            clientObject (object): The object that will contain all the sprites"""
        sprite_folders: list[str] = self.get_sprite_dirs()
        sprites_number: int = self.get_count_sprite_files(sprite_folders)
        
        # Create loading window if not provided
        if not self.loading_window and sprites_number > 0:
            self.loading_window = LoadingWindow(sprites_number)
            self.loading_window.show()
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as self.pool:
            for sprite_dir_name in sprite_folders:
                num_files = len(os.listdir(f"{image_path}sprites/{sprite_dir_name}"))
                sprite_files: list[str] = self.setup_sprite_files(sprite_dir_name, num_files)
                setattr(clientObject, f"{sprite_dir_name}_sprites", [])
                self.load_sprites(sprite_files, sprite_dir_name)
            
        infos_logger.log_infos("[PIXMAP]", f"Loaded sprites in {time.time() - start_time} seconds")
        
        # Close loading window if we created it
        if self.loading_window:
            self.loading_window.should_terminate = False
            self.loading_window.close()

    def get_sprite_dirs(self) -> list[str]:
        """Get all the sprite directories
        
        Returns:
            list[str]: A list of sprite directory names"""
        sprite_folders = []
        for root, dirs, files in os.walk(f"{image_path}sprites"):
            for dir in dirs:
                sprite_folders.append(dir)
        return sprite_folders
    
    def get_count_sprite_files(self, sprite_folders: list[str]) -> int:
        """Get the total number of sprite files in the given directories
        
        Args:
            sprite_folders (list[str]): A list of sprite directory names
        
        Returns:
            int: The total number of sprite files"""
        count = 0
        for sprite_dir_name in sprite_folders:
            count += len(os.listdir(f"{image_path}sprites/{sprite_dir_name}"))
        return count
    
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
        paths = [f"{image_path}sprites{filename}" for filename in sprite_files]
        size = sprite_size(sprite_dir_name)
        # The title screen is stretched to the window (LoopAnimatedLabel with IgnoreAspectRatio)
        mode = Qt.IgnoreAspectRatio if sprite_dir_name == "title_screen" else Qt.KeepAspectRatio
        # The files are read and shrunk by several threads at once (Qt does it without Python's lock)
        for pixmap_path, image in zip(paths, self.pool.map(lambda path: read_sprite(path, size, mode), paths)):
            # Update loading window with current file if available
            if self.loading_window:
                self.loaded_sprites += 1
                self.loading_window.update_progress(
                    self.loaded_sprites, 
                    os.path.basename(pixmap_path)
                )

            if image.isNull():
                infos_logger.log_infos("[PIXMAP]", f"Failed to load pixmap from: {pixmap_path}")
            else:
                sprites.append(QPixmap.fromImage(image))

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
        try:
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
        except RuntimeError as e:
            # The label was deleted (its screen was replaced) but its timer still runs:
            # just stop the timer, the label can't be touched anymore.
            infos_logger.log_infos("[ANIMATION]", f"Error in next_frame: {e}")
            self.timer.stop()
            self.current_sprite = 0

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

    def setup(self, parent: object, pixmap_name: str, frame_rate: int = 24):
        """Setup the loop animated label
        
        Args:
            parent (object): The parent object
            pixmap_name (str): The name of the pixmap
            frame_rate (int): The frame rate of the animation"""
        self.pixmap_name = pixmap_name
        self.sprites : list[QPixmap] = getattr(parent, f"{pixmap_name}_sprites")
        self.frame_rate = frame_rate
    
    def start_loop_animation(self):
        """Start the loop animation"""
        self.run_loop = True
        self.start_animation()

    def stop_loop_animation(self):
        """Stop the loop animation"""
        self.run_loop = False
        self.stop_animation()