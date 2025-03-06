import pygame
import os
import json
from shapely import Polygon
from geometry_utils import transform_shapes, inverse_transform_point, zoom_at, is_point_near_line
from geometry_utils import find_innermost_polygon, is_point_inside_polygon, shapely_to_pygame
from geometry_utils import find_midline_path, nearest_point_on_line, transform_point
from svg_parser import parse_svg, export_svg
from classes import Elevator, Stairs
from values import *
import xml.etree.ElementTree as ET
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

# Initialize pygame only once
# def init_pygame():
    # pygame.init()

class MapWindow:
    def __init__(self, file_path, map_name, width, height, entrances, spaces, walls, paths, circles, squares, on_close):    
        pygame.init()
        self.file_path = file_path
        self.map_name = map_name
        self.width = width
        self.height = height
        self.entrances = entrances
        self.spaces = spaces
        self.walls = walls
        self.paths = paths
        self.circles = circles
        self.squares = squares
        self.elevators = []  # List of Elevator objects
        self.stairs = []  # List of Stairs objects
        self.on_close = on_close
        
        # Create a new pygame window
        self.window_id = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.HWSURFACE)
        pygame.display.set_caption(f"Pather - {map_name}")
        
        # Initial colors and selection state
        self.entrance_colors = [ENTRANCE_COLOR] * len(entrances)
        self.space_colors = [SPACE_COLOR] * len(spaces)
        self.wall_colors = [WALL_COLOR] * len(walls)
        self.path_colors = [SPACE_COLOR] * len(paths)
        self.circle_colors = [SHAPE_COLOR] * len(circles)
        self.square_colors = [SHAPE_COLOR] * len(squares)
        self.selected_entrances = [False] * len(entrances)
        self.selected_spaces = [False] * len(spaces)
        self.selected_walls = [False] * len(walls)
        self.selected_paths = [False] * len(paths)
        self.midline_paths = []
        self.midline_colors = []
        
        # View control variables
        self.scale = 1.0
        self.offset = [0, 0]
        self.dragging = False
        self.drag_start = (0, 0)
        
        # Elevator mode
        self.elevator_mode = False
        self.current_elevator_id = 1

        # Stairs mode
        self.stairs_mode = False
        self.current_stairs_id = 1
        
        # Load saved spaces if they exist
        self.load_settings()
        
        # Start the rendering loop
        self.running = True
        self.run()
    
    def run(self):
        """Main loop for the map window"""
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

        # Notify the main application when this window closes
        self.on_close(self)
        
    
    def handle_events(self):
        """Handle pygame events for this window"""
        mouse_pos = pygame.mouse.get_pos()
        transformed_mouse_pos = inverse_transform_point(mouse_pos, self.scale, self.offset)
        
        # Handle hover effect if not in elevator mode
        if not self.elevator_mode or self.stairs_mode:
            handle_hover_and_click(transformed_mouse_pos, self.spaces, True, 
                                  self.space_colors, self.selected_spaces, SPACE_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

            if event.type == pygame.K_ESCAPE:
                self.close()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.scale, self.offset = zoom_at(self.scale, self.offset, mouse_pos, 1.1)
                elif event.button == 5:  # Scroll down
                    self.scale, self.offset = zoom_at(self.scale, self.offset, mouse_pos, 1.0 / 1.1)
                elif event.button == 2:  # Middle click
                    self.dragging = True
                    self.drag_start = event.pos
                elif event.button == 1:  # Left click
                    if self.elevator_mode:
                        # Check if clicking on existing elevator
                        clicked_elevator = False
                        for elevator in self.elevators:
                            if elevator.is_clicked(mouse_pos, self.scale, self.offset):
                                elevator.selected = not elevator.selected
                                clicked_elevator = True
                                break
                        
                        # If not clicking on existing elevator, create new one
                        if not clicked_elevator:
                            new_elevator = Elevator(transformed_mouse_pos, self.current_elevator_id)
                            self.elevators.append(new_elevator)
                            self.current_elevator_id += 1
                    elif self.stairs_mode:
                        # Check if clicking on existing stairs
                        clicked_stairs = False
                        for stairs in self.stairs:
                            if stairs.is_clicked(mouse_pos, self.scale, self.offset):
                                stairs.selected = not stairs.selected
                                clicked_stairs = True
                                break
                        
                        # If not clicking on existing stairs, create new one
                        if not clicked_stairs:
                            new_stairs = Stairs(transformed_mouse_pos, self.current_stairs_id)
                            self.stairs.append(new_stairs)
                            self.current_stairs_id += 1
                    
                    else:
                        # Normal space selection
                        handle_click(transformed_mouse_pos, self.spaces, True, 
                                    self.selected_spaces, self.space_colors, SPACE_COLOR)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Middle click
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx, dy = event.rel
                    self.offset[0] += dx
                    self.offset[1] += dy
            
            elif event.type == pygame.KEYDOWN:
                if event.key == KEY_MIDLINE:  # Calculate midline paths for selected spaces
                    self.midline_paths = handle_midline_path(
                        self.selected_spaces, self.spaces, self.entrances, self.walls)
                    self.midline_colors = [MIDLINE_COLOR] * len(self.midline_paths)
                    print(f"Midline paths: {len(self.midline_paths)}")
                
                elif event.key == KEY_ALL_MIDLINES:  # Calculate all midline paths
                    color_array, self.midline_paths = handle_all_midlines(self.spaces, self.entrances, 
                                                                         self.elevators, self.stairs)
                    self.midline_colors = color_array
                    print(f"All midline paths: {len(self.midline_paths)}")
                
                elif event.key == KEY_EXPORT:  # Export SVG
                    output_path = f"./output/{self.map_name}_output.svg"
                    export_svg(output_path, self.entrances, self.spaces, self.walls, 
                              self.midline_paths, elevators=self.elevators, stairs=self.stairs)
                    print(f"SVG exported as '{output_path}'")
                
                elif event.key == KEY_EXPORT_DEBUG:  # Export SVG with debug info
                    output_path = f"./output/{self.map_name}_debug.svg"
                    export_svg(output_path, self.entrances, self.spaces, self.walls, 
                              self.midline_paths, debug=True, midline_colors=self.midline_colors,
                              elevators=self.elevators)
                    print(f"SVG exported as '{output_path}' with debug info")
                
                elif event.key == KEY_SAVE:  # Save selected spaces
                    self.save_settings()
                
                elif event.key == KEY_LOAD:  # Load selected spaces
                    self.load_settings()
                
                elif event.key == KEY_ELEVATOR_MODE:  # Toggle elevator mode
                    if not self.stairs_mode:
                        self.elevator_mode = not self.elevator_mode
                    else:
                        self.stairs_mode = False
                        self.elevator_mode = True
                    print(f"Elevator mode {'enabled' if self.elevator_mode else 'disabled'}")
                
                elif event.key == KEY_STAIRS_MODE:  # Toggle stairs mode
                    if not self.elevator_mode:
                        self.stairs_mode = not self.stairs_mode
                    else:
                        self.elevator_mode = False
                        self.stairs_mode = True
                    print(f"Stairs mode {'enabled' if self.stairs_mode else 'disabled'}")
                
                elif event.key == KEY_ID_UP:  # Increment elevator ID
                    if self.elevator_mode:
                        self.current_elevator_id = min(self.current_elevator_id + 1, MAX_ELEVATOR_ID)
                        print(f"Current elevator ID: {self.current_elevator_id}")
                    elif self.stairs_mode:
                        self.current_stairs_id = min(self.current_stairs_id + 1, MAX_STAIRS_ID)
                        print(f"Current stairs ID: {self.current_stairs_id}")
                
                elif event.key == KEY_ID_DOWN:  # Decrement elevator ID
                    if self.elevator_mode:
                        self.current_elevator_id = max(self.current_elevator_id - 1, 1)
                        print(f"Current elevator ID: {self.current_elevator_id}")
                    elif self.stairs_mode:
                        self.current_stairs_id = max(self.current_stairs_id - 1, 1)
                        print(f"Current stairs ID: {self.current_stairs_id}")

                elif event.key == KEY_DELETE:  # Delete selected item
                    if self.elevator_mode:
                        self.elevators = [e for e in self.elevators if not e.selected]
                        print("Deleted selected elevators")
                    elif self.stairs_mode:
                        self.stairs = [s for s in self.stairs if not s.selected]
                        print("Deleted selected stairs")
                
                elif event.key == pygame.K_ESCAPE:  # Close window with ESC key
                    self.close()
            
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.window_id = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE | pygame.HWSURFACE)
    
    def close(self):
        """Properly close the window and notify the main application"""
        print(f"Closing window: {self.map_name}")
        self.running = False
    
    def draw(self):
        """Draw all elements to the screen"""
        self.window_id.fill((255, 255, 255))  # White background
        
        # Transform shapes
        transformed_spaces = transform_shapes(self.spaces, self.scale, self.offset)
        transformed_walls = transform_shapes(self.walls, self.scale, self.offset)
        transformed_entrances = transform_shapes(self.entrances, self.scale, self.offset)
        transformed_midline_paths = transform_shapes(self.midline_paths, self.scale, self.offset)
        transformed_circles = transform_shapes(self.circles, self.scale, self.offset)
        transformed_squares = transform_shapes(self.squares, self.scale, self.offset)
        
        # Draw shapes
        draw_shapes(self.window_id, transformed_spaces, True, self.space_colors)
        draw_shapes(self.window_id, transformed_walls, False, self.wall_colors)
        draw_shapes(self.window_id, transformed_entrances, False, self.entrance_colors)
        draw_shapes(self.window_id, transformed_midline_paths, False, self.midline_colors)        
        draw_shapes(self.window_id, transformed_circles, False, self.circle_colors)
        draw_shapes(self.window_id, transformed_squares, False, self.square_colors)

        # Draw elevators
        for elevator in self.elevators:
            elevator.draw(self.window_id, self.scale, self.offset)

        # Draw stairs
        for stairs in self.stairs:
            stairs.draw(self.window_id, self.scale, self.offset)
        
        # Draw elevator mode indicator
        if self.elevator_mode:
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(f"Elevator Mode (ID: {self.current_elevator_id})", True, ELEVATOR_COLOR)
            self.window_id.blit(text, (10, 10))
        elif self.stairs_mode:
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(f"Stairs Mode (ID: {self.current_stairs_id})", True, STAIRS_COLOR)
            self.window_id.blit(text, (10, 10))
    
    def save_settings(self):
        """Save selected elevators to a JSON file"""
        file_path = f"./output/{self.map_name}_settings.json"
        with open(file_path, 'w') as file:
            json.dump({
                "elevators": [{"position": e.position, "id": e.id, "selected": e.selected} 
                             for e in self.elevators],
                "stairs": [{"position": s.position, "id": s.id, "selected": s.selected} 
                             for s in self.stairs],
            }, file)
        print(f"Selected elevators saved to {file_path}")
    
    def load_settings(self):
        """Load selected elevators from a JSON file"""
        file_path = f"./output/{self.map_name}_settings.json"
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Load elevators
                loaded_elevators = data.get("elevators", [])
                if loaded_elevators:
                    self.elevators = []
                    for e_data in loaded_elevators:
                        elevator = Elevator(
                            position=tuple(e_data["position"]), 
                            elevator_id=e_data.get("id", 1)
                        )
                        elevator.selected = e_data.get("selected", False)
                        self.elevators.append(elevator)
                
                # Load stairs
                loaded_stairs = data.get("stairs", [])
                if loaded_stairs:
                    self.stairs = []
                    for e_data in loaded_stairs:
                        staircase = Stairs(
                            position=tuple(e_data["position"]), 
                            stairs_id=e_data.get("id", 1)
                        )
                        staircase.selected = e_data.get("selected", False)
                        self.stairs.append(staircase)
                
                print(f"Selected elevators loaded from {file_path}")
        except FileNotFoundError:
            print(f"No saved file found at {file_path}")

# Existing functions from display.py with minor modifications
def draw_shapes(screen, shapes, is_polygon, colors):
    """
    Draws polygons and polylines on the screen.
    """
    for i, shape in enumerate(shapes):
        if is_polygon:
            pygame.draw.polygon(screen, colors[i], shape)
        else:
            pygame.draw.lines(screen, colors[i], False, shape, 3)

def handle_hover_and_click(mouse_pos, shapes, is_polygon, shape_colors, selected, base_color):
    """
    Handles highlighting shapes when the mouse hovers over them.
    """
    if is_polygon:
        innermost_shape = find_innermost_polygon(mouse_pos, shapes)
        for i, shape in enumerate(shapes):
            if shape == innermost_shape:
                if not selected[i]:
                    shape_colors[i] = HIGHLIGHT_COLOR
            elif not selected[i]:
                shape_colors[i] = base_color
    else:
        for i, shape in enumerate(shapes):
            if is_point_near_line(mouse_pos, shape):
                if not selected[i]:
                    shape_colors[i] = HIGHLIGHT_COLOR
            elif not selected[i]:
                shape_colors[i] = base_color

def handle_click(mouse_pos, shapes, is_polygon, selected, shape_colors, base_color):
    """
    Handles selecting/deselecting shapes when clicked.
    """
    if is_polygon:
        innermost_shape = find_innermost_polygon(mouse_pos, shapes)
        for i, shape in enumerate(shapes):
            if shape == innermost_shape:
                selected[i] = not selected[i]
                shape_colors[i] = CLICKED_COLOR if selected[i] else base_color
                print(i + 1, selected[i])
    else:
        for i, shape in enumerate(shapes):
            if is_point_near_line(mouse_pos, shape):
                selected[i] = not selected[i]
                shape_colors[i] = CLICKED_COLOR if selected[i] else base_color

def handle_midline_path(selected_spaces, spaces, entrances, walls, elevators, stairs):
    """
    Calculates midline paths for selected spaces and connects entrances to these paths.
    """
    midline_paths = []
    for i, selected in enumerate(selected_spaces):
        if selected:
            print("Selected space:", i + 1)
            midline_path = find_midline_path(polygon=spaces[i])
            if isinstance(midline_path, list) and all(isinstance(item, list) for item in midline_path):
                midline_paths.extend(midline_path)
            else:
                midline_paths.append(midline_path)

            if not midline_path:
                continue

            # Add paths from doors to the nearest point on the midline if it touches the space
            for entrance in entrances:
                midpoint = ((entrance[0][0] + entrance[1][0]) / 2, (entrance[0][1] + entrance[1][1]) / 2)
                if is_point_inside_polygon(midpoint, spaces[i], tolerance=5):
                    nearest_point = nearest_point_on_line(midpoint, midline_path)
                    midline_paths.append([tuple(midpoint), tuple(nearest_point)])

            # Add paths from elevators to the nearest point on the midline
            for elevator in elevators:
                if is_point_inside_polygon(elevator.position, spaces[i], tolerance=5):
                    nearest_point = nearest_point_on_line(elevator.position, midline_path)
                    midline_paths.append([tuple(elevator.position), tuple(nearest_point)])

            # Add paths from stairs to the nearest point on the midline
            for stair in stairs:
                if is_point_inside_polygon(stair.position, spaces[i], tolerance=5):
                    nearest_point = nearest_point_on_line(stair.position, midline_path)
                    midline_paths.append([tuple(stair.position), tuple(nearest_point)])
    
    return midline_paths

def handle_all_midlines(spaces, entrances, elevators=None, stairs=None):
    """
    Calculates midline paths for all spaces and connects them.
    """
    midline_paths = handle_midline_path([True] * len(spaces), spaces, entrances, [], elevators, stairs)
    paths = midline_paths.copy()

    # Merge all midlines that share coordinates
    merged_midlines = []
    while paths:
        current_path = paths.pop(0)
        overlapping_indices = [i for i, path in enumerate(merged_midlines) if any(coord in path for coord in current_path)]
        
        if overlapping_indices:
            # Merge all overlapping midlines into one
            merged_path = current_path
            for index in sorted(overlapping_indices, reverse=True):
                merged_path = list(set(merged_path + merged_midlines.pop(index)))
            merged_midlines.append(merged_path)
        else:
            merged_midlines.append(current_path)

    # Find the largest midline
    largest_midline = max(merged_midlines, key=len, default=[])
    largest_midline_set = set(map(tuple, largest_midline))

    color_array = []
    for midline in midline_paths:
        color_array.append((0, 255, 0) if any(point in largest_midline_set for point in midline) else (255, 0, 0))

    return color_array, midline_paths