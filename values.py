import pygame

# Colors Constants
ENTRANCE_COLOR = (0, 100, 255)  # Blue
SPACE_COLOR = (0, 100, 100)  # Green
WALL_COLOR = (200, 200, 200)  # Gray
HIGHLIGHT_COLOR = (50, 50, 50)  # Darker
CLICKED_COLOR = (0, 150, 150)  # Orange
MIDLINE_COLOR = (255, 0, 0)  # Red
ELEVATOR_COLOR = (255, 0, 255)  # Magenta
ELEVATOR_SELECTED_COLOR = (255, 150, 255)  # Light Magenta
STAIRS_COLOR = (200, 200, 0)  # Yellow
STAIRS_SELECTED_COLOR = (255, 255, 0)  # Light Yellow
SHAPE_COLOR = (0, 0, 0)  # Black

# Path Constants
INPUT_PATH = "./ver-0.0.4-svgs/three.svg"  # Replace with your SVG file path
OUTPUT_PATH = "./output/output.svg"  # Replace with your output SVG file path

# Keyboard Shortcuts
KEY_MIDLINE = pygame.K_m  # Calculate midline paths for selected spaces
KEY_ALL_MIDLINES = pygame.K_a  # Calculate all midline paths
KEY_EXPORT = pygame.K_e  # Export SVG
KEY_EXPORT_DEBUG = pygame.K_r  # Export SVG with debug info
KEY_SAVE = pygame.K_s  # Save selected spaces
KEY_LOAD = pygame.K_l  # Load selected spaces
KEY_STAIRS_MODE = pygame.K_c  # Toggle stairs mode
KEY_ELEVATOR_MODE = pygame.K_v  # Toggle elevator mode
KEY_ID_UP = pygame.K_UP  # Increment elevator ID
KEY_ID_DOWN = pygame.K_DOWN  # Decrement elevator ID
KEY_DELETE = pygame.K_DELETE  # Delete selected elevator

# Elevator Constants
MAX_ELEVATOR_ID = 99  # Maximum elevator ID

# Stairs Constants
MAX_STAIRS_ID = 99  # Maximum stairs ID