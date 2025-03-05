import pygame
from shapely import Polygon
from geometry_utils import transform_shapes, inverse_transform_point, zoom_at, is_point_near_line
from geometry_utils import find_innermost_polygon, is_point_inside_polygon, shapely_to_pygame
from geometry_utils import find_midline_path, nearest_point_on_line
from svg_parser import parse_svg, export_svg
from values import *
import xml.etree.ElementTree as ET
import json
import os
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

def draw_shapes(screen, shapes, is_polygon, colors):
    """
    Draws polygons and polylines on the screen.
    
    Parameters:
        screen: Pygame display surface
        shapes: List of shapes to draw
        is_polygon: Boolean indicating if shapes are polygons (True) or polylines (False)
        colors: List of RGB color tuples for each shape
    """
    for i, shape in enumerate(shapes):
        if is_polygon:
            pygame.draw.polygon(screen, colors[i], shape)
        else:
            pygame.draw.lines(screen, colors[i], False, shape, 3)

def handle_hover_and_click(mouse_pos, shapes, is_polygon, shape_colors, selected, base_color):
    """
    Handles highlighting shapes when the mouse hovers over them.
    
    Parameters:
        mouse_pos: Current mouse position (x, y)
        shapes: List of shapes to check for hovering
        is_polygon: Boolean indicating if shapes are polygons (True) or polylines (False)
        shape_colors: List of RGB color tuples for each shape
        selected: List of boolean values indicating if a shape is selected
        base_color: Default color to reset shapes to when not hovered
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
    
    Parameters:
        mouse_pos: Current mouse position (x, y)
        shapes: List of shapes to check for clicking
        is_polygon: Boolean indicating if shapes are polygons (True) or polylines (False)
        selected: List of boolean values indicating if a shape is selected
        shape_colors: List of RGB color tuples for each shape
        base_color: Default color to reset shapes to when not selected
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

def handle_midline_path(selected_spaces, spaces, entrances, walls):
    """
    Calculates midline paths for selected spaces and connects entrances to these paths.
    
    Parameters:
        selected_spaces: List of boolean values indicating if a space is selected
        spaces: List of space polygons
        entrances: List of entrance polylines
        walls: List of wall polylines
        
    Returns:
        List of midline paths
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
    
    return midline_paths

def handle_all_midlines(spaces, entrances):
    """
    Calculates midline paths for all spaces and connects them.
    
    Parameters:
        spaces: List of space polygons
        entrances: List of entrance polylines
        
    Returns:
        Tuple containing (color_array, midline_paths) where:
            - color_array: List of RGB color tuples for the midline paths
            - midline_paths: List of midline paths
    """
    midline_paths = handle_midline_path([True] * len(spaces), spaces, entrances, [])
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

def save_selected_spaces(file_path, selected_spaces):
    """
    Saves the selected spaces to a JSON file.
    
    Parameters:
        file_path: Path to save the file
        selected_spaces: List of boolean values indicating if a space is selected
    """
    with open(file_path, 'w') as file:
        json.dump(selected_spaces, file)
    print(f"Selected spaces saved to {file_path}")

def load_selected_spaces(file_path, selected_spaces, space_colors, base_color):
    """
    Loads the selected spaces from a JSON file.
    
    Parameters:
        file_path: Path to load the file from
        selected_spaces: List to update with loaded selected spaces
        space_colors: List of RGB color tuples for each space
        base_color: Default color for unselected spaces
        
    Returns:
        List of boolean values indicating if a space is selected, or None if the file was not found
    """
    try:
        with open(file_path, 'r') as file:
            loaded_selected_spaces = json.load(file)
        print(f"Selected spaces loaded from {file_path}")
        
        for i, selected in enumerate(loaded_selected_spaces):
            selected_spaces[i] = selected
            space_colors[i] = CLICKED_COLOR if selected else base_color
        
        return loaded_selected_spaces
    except FileNotFoundError:
        print(f"No saved file found at {file_path}")
        return None

def display_shapes(width, height, entrances, spaces, walls, paths, load=True):
    """
    Main interactive display function for visualizing and manipulating shapes.
    
    Parameters:
        width: Width of the display window
        height: Height of the display window
        entrances: List of entrance polylines
        spaces: List of space polygons
        walls: List of wall polylines
        paths: List of path polylines
        load: Boolean indicating whether to load previously saved selected spaces
    """
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("SVG Viewer")

    # Initial colors and selection state
    entrance_colors = [ENTRANCE_COLOR] * len(entrances)
    space_colors = [SPACE_COLOR] * len(spaces)
    wall_colors = [WALL_COLOR] * len(walls)
    path_colors = [SPACE_COLOR] * len(paths)
    selected_entrances = [False] * len(entrances)
    selected_spaces = [False] * len(spaces)
    selected_walls = [False] * len(walls)
    selected_paths = [False] * len(paths)
    midline_paths = []
    midline_colors = []

    # Load previously saved selected spaces
    if load:
        loaded_selected_spaces = load_selected_spaces("selected_spaces.json", selected_spaces, space_colors, SPACE_COLOR)
        if loaded_selected_spaces is not None:
            selected_spaces = loaded_selected_spaces

    scale = 1.0
    offset = [0, 0]
    dragging = False
    drag_start = (0, 0)

    running = True
    while running:
        screen.fill((255, 255, 255))  # White background
        mouse_pos = pygame.mouse.get_pos()

        # Handle hover effect
        transformed_mouse_pos = inverse_transform_point(mouse_pos, scale, offset)
        handle_hover_and_click(transformed_mouse_pos, spaces, True, space_colors, selected_spaces, SPACE_COLOR)

        # Transform shapes
        transformed_spaces = transform_shapes(spaces, scale, offset)
        transformed_walls = transform_shapes(walls, scale, offset)
        transformed_entrances = transform_shapes(entrances, scale, offset)
        transformed_midline_paths = transform_shapes(midline_paths, scale, offset)

        # Draw everything
        draw_shapes(screen, transformed_spaces, True, space_colors)
        draw_shapes(screen, transformed_walls, False, wall_colors)
        draw_shapes(screen, transformed_entrances, False, entrance_colors)
        draw_shapes(screen, transformed_midline_paths, False, midline_colors)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    scale, offset = zoom_at(scale, offset, mouse_pos, 1.1)
                elif event.button == 5:  # Scroll down
                    scale, offset = zoom_at(scale, offset, mouse_pos, 1.0 / 1.1)
                elif event.button == 2:  # Middle click
                    dragging = True
                    drag_start = event.pos
                else:
                    handle_click(transformed_mouse_pos, spaces, True, selected_spaces, space_colors, SPACE_COLOR)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Middle click
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx, dy = event.rel
                    offset[0] += dx
                    offset[1] += dy
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # Press 'm' to calculate midline paths
                    midline_paths = handle_midline_path(selected_spaces, spaces, entrances, walls)
                    midline_colors = [MIDLINE_COLOR] * len(midline_paths)
                    print(f"Midline paths: {len(midline_paths)}")
                elif event.key == pygame.K_a:  # Press 'a' to calculate all midline paths
                    color_array, midline_paths = handle_all_midlines(spaces, entrances)
                    midline_colors = color_array
                    print(f"All midline paths: {len(midline_paths)}")
                elif event.key == pygame.K_e:  # Press 'e' to export the SVG
                    export_svg(OUTPUT_PATH, entrances, spaces, walls, midline_paths)
                    print(f"SVG exported as '{OUTPUT_PATH}'")
                elif event.key == pygame.K_r:  # Press 'r' to export the SVG with debug info
                    export_svg(OUTPUT_PATH, entrances, spaces, walls, midline_paths, debug=True, midline_colors=midline_colors)
                    print(f"SVG exported as '{OUTPUT_PATH}' with debug info")
                elif event.key == pygame.K_s:  # Press 's' to save selected spaces
                    save_selected_spaces("selected_spaces.json", selected_spaces)
                elif event.key == pygame.K_l:  # Press 'l' to load selected spaces
                    loaded_selected_spaces = load_selected_spaces("selected_spaces.json", selected_spaces, space_colors, SPACE_COLOR)
                    if loaded_selected_spaces is not None:
                        selected_spaces = loaded_selected_spaces
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    pygame.quit()