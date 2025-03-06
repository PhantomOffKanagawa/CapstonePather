import pygame
from geometry_utils import transform_point
from values import ELEVATOR_COLOR, ELEVATOR_SELECTED_COLOR
from values import STAIRS_COLOR, STAIRS_SELECTED_COLOR
from xml.etree import ElementTree as ET

class Elevator:
    def __init__(self, position, elevator_id=1):
        self.position = position  # (x, y) tuple
        self.id = elevator_id
        self.selected = False
        self.radius = 8  # Radius for drawing
    
    def is_clicked(self, point, scale, offset):
        # Check if a point is within the elevator's circle
        x1, y1 = self.position
        x2, y2 = point
        x1, y1 = transform_point((x1, y1), scale, offset)
        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        return distance <= self.radius * scale

    def draw(self, screen, scale, offset):
        # Draw elevator circle
        x, y = transform_point(self.position, scale, offset)
        color = ELEVATOR_SELECTED_COLOR if self.selected else ELEVATOR_COLOR
        pygame.draw.circle(screen, color, (int(x), int(y)), int(self.radius * scale))
        
        # Draw elevator ID text
        font = pygame.font.SysFont('Arial', int(12 * scale))
        text = font.render(str(self.id), True, (255, 255, 255))
        text_rect = text.get_rect(center=(int(x), int(y)))
        screen.blit(text, text_rect)

    def export(self):
        """Creates an SVG circle element at the specified position with the given radius and color."""
        cx, cy = self.position
        attrs = {
            'cx': str(cx),
            'cy': str(cy),
            'r': str(self.radius),
            'adjacency': str(self.id)
        }
        
        attrs['data-id'] = str(self.id)
            
        circle = ET.Element('circle', **attrs)
        
        # Create text element for the ID
        text_attrs = {
            'x': str(cx),
            'y': str(cy),
            'text-anchor': 'middle',
            'dy': '.3em',  # Adjust vertical alignment
            'style': 'font-size:12px; fill: white;'
        }
        text = ET.Element('text', **text_attrs)
        text.text = str(self.id)
        
        return (circle, text)


class Stairs:
    def __init__(self, position, stairs_id=1):
        self.position = position  # (x, y) tuple
        self.id = stairs_id
        self.selected = False
        self.radius = 8  # Radius for drawing
    
    def is_clicked(self, point, scale, offset):
        # Check if a point is within the stairs' area (assuming a rectangular area)
        x1, y1 = self.position
        x2, y2 = point
        x1, y1 = transform_point((x1, y1), scale, offset)
        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        return distance <= self.radius * 2 * scale

    def draw(self, screen, scale, offset):
        # Draw stairs rectangle
        x, y = transform_point(self.position, scale, offset)
        width, height = self.radius * 2 * scale, self.radius * 2 * scale
        color = STAIRS_SELECTED_COLOR if self.selected else STAIRS_COLOR
        pygame.draw.rect(screen, color, (int(x - width / 2), int(y - height / 2), int(width), int(height)))
        
        # Draw stairs ID text
        font = pygame.font.SysFont('Arial', int(12 * scale))
        text = font.render(str(self.id), True, (255, 255, 255))
        text_rect = text.get_rect(center=(int(x), int(y)))
        screen.blit(text, text_rect)

    def export(self):
        """Creates an SVG circle element at the specified position with the given width, height, and color."""
        cx, cy = self.position
        attrs = {
            'cx': str(cx),
            'cy': str(cy),
            'r': str(self.radius),
            'adjacency': str(self.id)
        }
        
        attrs['data-id'] = str(self.id)
            
        circle = ET.Element('circle', **attrs)
        
        # Create text element for the ID
        text_attrs = {
            'x': str(cx),
            'y': str(cy),
            'text-anchor': 'middle',
            'dy': '.3em',  # Adjust vertical alignment
            'style': 'font-size:12px; fill: white;'
        }
        text = ET.Element('text', **text_attrs)
        text.text = str(self.id)
        
        return (circle, text)