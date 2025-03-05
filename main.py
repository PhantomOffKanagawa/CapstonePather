import os
from svg_parser import parse_svg
from display import display_shapes
from values import INPUT_PATH

def main():
    """
    Main entry point for the application.
    Parses an SVG file and displays its contents interactively.
    """
    file_path = INPUT_PATH  
    
    # Parse the SVG file to extract entrances, spaces, walls, and paths
    width, height, entrances, spaces, walls, paths = parse_svg(file_path)
    
    print(f"Entrances: {len(entrances)}, Spaces: {len(spaces)}, Walls: {len(walls)}, Paths: {len(paths)}")
    
    # Display the shapes in an interactive window
    display_shapes(width, height, entrances, spaces, walls, paths, load=False)

if __name__ == "__main__":
    main()