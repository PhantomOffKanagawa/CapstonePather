# Pather - SVG Map Annotation Tool

## Overview

Pather is a tool for annotating SVG maps of buildings by:
- Visualizing floor plans with walls, spaces, and entrances
- Generating centerline/midline paths through spaces
- Connecting doors to midline paths
- Exporting updated SVG files with pathways for navigation

This tool is built primarily for a university project related to an indoor navigation application.

This tool was rapidly prototyped alongside GitHub copilot in VS Code. Most PyGame visualization functions were developed primarily with this tool while most functionality was developed with minimal input.

## Features

- **Interactive Visualization**: Pan, zoom, and select spaces in your SVG floor plans
- **Automatic Midline Generation**: Calculate the center paths through rooms and corridors using pygeoops
- **Space Selection**: Select individual spaces to generate paths for
- **Path Connection**: Automatically connects entrances (doors) to the nearest midline
- **SVG Export**: Save your work as an SVG file with all annotations
- **State Saving**: Save and load your space selections

## Prerequisites

- Python 3.7+
- Dependencies:
  - pygame
  - numpy
  - shapely
  - pygeoops
  - tkinter

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install pygame numpy shapely pygeoops tkinter
```

## Usage

### Configuration

Edit the `values.py` file to adjust:
- Input SVG file path
- Output SVG file path
- Display colors

### Running the Application

```bash
python main.py
```

### Controls

- **Left Click**: Select/deselect spaces
- **Middle Click + Drag**: Pan the view
- **Mouse Wheel**: Zoom in/out
- **Keys**:
  - `m`: Calculate midline paths for selected spaces
  - `a`: Calculate all midline paths
  - `s`: Save selected spaces
  - `l`: Load selected spaces
  - `e`: Export SVG
  - `r`: Export SVG with debug information
  - `v`: Activate "Elevator Mode"
  - `c`: Activate "Stairs Mode"
  - `up arrow`: Increase ID
  - `down arrow`: Decrease ID
  - `delete`: Delete selected Elevator or Stairs

## SVG Format Requirements

The input SVG should have the following structure:
- `<g id="spaces">`: Group containing space/room polygons
- `<g id="walls">`: Group containing wall polylines
- `<g id="entrances">`: Group containing entrance/door polylines
- `<g id="shapes">`: (Optional) Group with shapes for stairs and elevators
- `<g id="windows">`: (Optional) Group with polylines for windows, unused here

## SVG Export Parameters

The exported SVG will have the same structure with the following added or modified groups:
- `<g id="midlines">`: Group with polylines representing midline path
- `<g id="elevators">`: Group with circles representing elevators, adjacency attribute shows floor global connections
- `<g id="stairs">`: Group with circles representing stairs, adjacency attribute shows floor global connections
- `<g id="text">`: Group with text for elevator/stairs IDs for readability
~~- `<g id="shapes">`: Removed~~
~~- `<g id="windows">`: Removed~~

## Examples

1. Load an SVG floor plan
2. Select spaces of interest by clicking on them
3. Press `m` to generate midline paths through selected spaces
4. Press `e` to export the annotated SVG

## Future Roadmap

- [X] ~~Add support for stairs and elevators~~
- [X] ~~Connect multiple floors through vertical transportation element adjacency~~
- [ ] Add room name annotations
- [ ] Improve path optimization and smoothing
- [ ] Multi floor editing simultaneously
- [ ] Refactor an Cleanup

## Project Structure

- `main.py`: Entry point
- `values.py`: Configuration constants
- `svg_parser.py`: SVG parsing and export functions
- `display.py`: Interactive display and UI logic
- `geometry_utils.py`: Geometric calculations and transformations
- `classes.py`: Holds data for classes like elevator

## License

GNU General Public License v3.0
