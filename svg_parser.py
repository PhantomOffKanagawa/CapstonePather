import xml.etree.ElementTree as ET
from values import *
import itertools

def parse_svg(file_path, screen_width=800, screen_height=600):
    """
    Extracts polylines under 'entrances' and 'walls', polygons under 'spaces', and paths.
    
    Parameters:
        file_path: Path to the SVG file
        screen_width: Width of the display window
        screen_height: Height of the display window
        
    Returns:
        Tuple containing (screen_width, screen_height, entrances, spaces, walls, paths)
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'svg': 'http://www.w3.org/2000/svg'}

    # Default SVG dimensions
    svg_width = int(root.get('width', screen_width))
    svg_height = int(root.get('height', screen_height))

    entrances = extract_shapes(root, namespace, "entrances", "polyline")
    spaces = extract_shapes(root, namespace, "spaces", "polygon")
    walls = extract_shapes(root, namespace, "walls", "polyline")
    paths = extract_shapes(root, namespace, "*", "path")

    # Normalize points
    all_shapes = entrances + spaces + walls + paths
    max_x = max((p[0] for shape in all_shapes for p in shape), default=svg_width)
    max_y = max((p[1] for shape in all_shapes for p in shape), default=svg_height)

    return screen_width, screen_height, [normalize(s, max_x, max_y, screen_width, screen_height) for s in entrances], [normalize(s, max_x, max_y, screen_width, screen_height) for s in spaces], [normalize(s, max_x, max_y, screen_width, screen_height) for s in walls], [normalize(s, max_x, max_y, screen_width, screen_height) for s in paths]

def extract_shapes(root, namespace, group_id, tag):
    """
    Extracts either polylines, polygons, or paths from a specific group.
    
    Parameters:
        root: Root element of the SVG tree
        namespace: XML namespace
        group_id: ID of the group to extract from (or "*" for all)
        tag: Type of element to extract ("polyline", "polygon", or "path")
        
    Returns:
        List of shapes, where each shape is a list of (x, y) tuples
    """
    if group_id == "*":
        group = root
    else:
        group = root.find(f".//{{http://www.w3.org/2000/svg}}g[@id='{group_id}']", namespace)
        
    shapes = []
    if group is not None:
        for element in group.findall(f"{{http://www.w3.org/2000/svg}}{tag}", namespace):
            if tag == 'path':
                d_attr = element.get('d', '')
                points = parse_path(d_attr, shapes)
            else:
                points_attr = element.get('points', '')
                points = [(float(x), float(y)) for x, y in (p.split(',') for p in points_attr.split())]
            if points:
                shapes.append(points)
    return shapes

def parse_path(d_attr, shapes):
    """
    Parses the 'd' attribute of a path element into a list of points.
    
    Parameters:
        d_attr: Value of the 'd' attribute in an SVG path
        shapes: List to append parsed shapes to
        
    Returns:
        List of (x, y) tuples representing the path
    """
    import re
    path_commands = re.findall(r'[MLHVCSQTAZmlhvcsqtaz][^MLHVCSQTAZmlhvcsqtaz]*', d_attr)
    points = []
    current_pos = (0, 0)
    start_pos = (0, 0)
    for (n, command) in enumerate(path_commands):
        cmd_type = command[0]
        cmd_values = list(map(float, re.findall(r'-?\d+\.?\d*', command[1:])))
        if cmd_type in 'Mm':
            if (len(points) != 0):
                shapes.append(points)
                points = []
                start_pos = (0, 0)
            for i in range(0, len(cmd_values), 2):
                x, y = cmd_values[i:i+2]
                if cmd_type == 'm':
                    x += current_pos[0]
                    y += current_pos[1]
                current_pos = (x, y)
                if start_pos == (0, 0):
                    start_pos = current_pos
                points.append(current_pos)
        elif cmd_type in 'Ll':
            for i in range(0, len(cmd_values), 2):
                x, y = cmd_values[i:i+2]
                if cmd_type == 'l':
                    x += current_pos[0]
                    y += current_pos[1]
                current_pos = (x, y)
                points.append(current_pos)
        elif cmd_type in 'Hh':
            for x in cmd_values:
                if cmd_type == 'h':
                    x += current_pos[0]
                current_pos = (x, current_pos[1])
                points.append(current_pos)
        elif cmd_type in 'Vv':
            for y in cmd_values:
                if cmd_type == 'v':
                    y += current_pos[1]
                current_pos = (current_pos[0], y)
                points.append(current_pos)
        elif cmd_type in 'Zz':
            current_pos = start_pos
            points.append(current_pos)
    return points

def normalize(shape, max_x, max_y, screen_width, screen_height):
    """
    Normalizes shape coordinates to fit within screen dimensions.
    
    Parameters:
        shape: List of (x, y) tuples
        max_x: Maximum x-coordinate in the original SVG
        max_y: Maximum y-coordinate in the original SVG
        screen_width: Width of the display window
        screen_height: Height of the display window
        
    Returns:
        List of normalized (x, y) tuples
    """
    return [(int(x / max_x * screen_width), int(y / max_y * screen_height)) for x, y in shape]

def export_svg(file_path, entrances, spaces, walls, midlines, debug=False, midline_colors=None):
    """
    Exports shapes to an SVG file.
    
    Parameters:
        file_path: Path where the SVG will be saved
        entrances: List of entrance polylines
        spaces: List of space polygons
        walls: List of wall polylines
        midlines: List of midline paths
        debug: Whether to include debug information (default: False)
        midline_colors: Colors for midlines if in debug mode (default: None)
    """
    svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", width="800", height="600")
    
    def create_polyline(points, color):
        """Creates an SVG polyline element with the given points and color."""
        polyline = ET.Element('polyline', points=" ".join(f"{x},{y}" for x, y in points))
        polyline.set('style', f"fill:none;stroke:rgb{color};stroke-width:2")
        return polyline

    def create_polygon(points, color):
        """Creates an SVG polygon element with the given points and color."""
        polygon = ET.Element('polygon', points=" ".join(f"{x},{y}" for x, y in points))
        polygon.set('style', f"fill:none;stroke:rgb{color};stroke-width:2")
        return polygon

    def create_circle(cx, cy, radius, color):
        """Creates an SVG circle element at the specified position with the given radius and color."""
        circle = ET.Element('circle', cx=str(cx), cy=str(cy), r=str(radius))
        circle.set('style', f"fill:rgb{color};stroke:none")
        return circle

    # Create groups
    entrances_group = ET.Element('g', id="entrances", style=f"fill:none;stroke:rgb{ENTRANCE_COLOR};stroke-width:2")
    spaces_group = ET.Element('g', id="spaces", style=f"fill:none;stroke:rgb{SPACE_COLOR};stroke-width:2")
    walls_group = ET.Element('g', id="walls", style=f"fill:none;stroke:rgb{WALL_COLOR};stroke-width:2")
    midlines_group = ET.Element('g', id="midlines", style=f"fill:none;stroke:rgb{MIDLINE_COLOR};stroke-width:2")
    debug_group = ET.Element('g', id="debug")

    # Add entrances
    for entrance in entrances:
        entrances_group.append(create_polyline(entrance, ENTRANCE_COLOR))

    # Add spaces
    for space in spaces:
        spaces_group.append(create_polygon(space, SPACE_COLOR))

    # Add walls
    for wall in walls:
        walls_group.append(create_polyline(wall, WALL_COLOR))

    # Add midlines
    if debug:
        if midline_colors:
            colors = midline_colors.copy()
        else:
            colors = itertools.cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255)])

        for midline in midlines:
            if not midline_colors:
                color = next(colors)
            else:
                color = colors.pop(0)

            midlines_group.append(create_polyline(midline, color))
    else:
        for midline in midlines:
            midlines_group.append(create_polyline(midline, MIDLINE_COLOR))

    # Append groups to SVG
    svg.append(spaces_group)
    svg.append(walls_group)
    svg.append(entrances_group)
    svg.append(midlines_group)
    if debug:
        svg.append(debug_group)

    tree = ET.ElementTree(svg)
    tree.write(file_path)