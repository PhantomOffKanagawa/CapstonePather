# Pather - SVG Map Annotation Tool

## Overview

Pather is a tool for annotating SVG maps of buildings by:
- Visualizing floor plans with walls, spaces, and entrances
- Generating centerline/midline paths through spaces
- Connecting doors to midline paths
- Exporting updated SVG files with pathways for navigation

This tool is built primarily for a university project related to an indoor navigation application.

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

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install pygame numpy shapely pygeoops
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

## SVG Format Requirements

The input SVG should have the following structure:
- `<g id="spaces">`: Group containing space/room polygons
- `<g id="entrances">`: Group containing entrance/door polylines
- `<g id="walls">`: Group containing wall polylines

## Examples

1. Load an SVG floor plan
2. Select spaces of interest by clicking on them
3. Press `m` to generate midline paths through selected spaces
4. Press `e` to export the annotated SVG

## Future Roadmap

- [ ] Add support for stairs and elevators
- [ ] Add room name annotations
- [ ] Improve path optimization and smoothing
- [ ] Connect multiple floors through vertical transportation elements
- [ ] Multi floor editing simultaneously

## Project Structure

- `main.py`: Entry point
- `values.py`: Configuration constants
- `svg_parser.py`: SVG parsing and export functions
- `display.py`: Interactive display and UI logic
- `geometry_utils.py`: Geometric calculations and transformations

## License

GNU General Public License v3.0