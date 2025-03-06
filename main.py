import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import threading
from svg_parser import parse_svg
from display import MapWindow
from values import *

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Pather - SVG Map Annotation Tool")
        self.root.geometry("500x300")
        
        self.current_window = None
        
        # Create menu bar
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open SVG", command=self.open_svg)
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.root.config(menu=menubar)
        
        # Add welcome message
        welcome_label = tk.Label(root, text="Welcome to Pather\nSVG Map Annotation Tool", font=("Arial", 16))
        welcome_label.pack(pady=20)
        
        # Add open button
        open_button = tk.Button(root, text="Open SVG Map", command=self.open_svg, height=2, width=20)
        open_button.pack(pady=10)
        
        # Initialize pygame
        # init_pygame()
        
        # Check for output directory
        os.makedirs("./output", exist_ok=True)
        
    def open_svg(self):
        # If there's an existing window, close it first
        if self.current_window and self.current_window.running:
            self.current_window.close()
            self.current_window = None

        file_path = filedialog.askopenfilename(
            initialdir="./",
            title="Select SVG file",
            filetypes=(("SVG files", "*.svg"), ("all files", "*.*"))
        )
        
        if file_path:
            try:
                # Get map name from file path
                map_name = os.path.splitext(os.path.basename(file_path))[0]
                
                # Parse the SVG file
                width, height, entrances, spaces, walls, paths, elevators, stairs = parse_svg(file_path)
                
                # Create a new map window
                self.current_window = MapWindow(
                    file_path=file_path,
                    map_name=map_name,
                    width=width,
                    height=height,
                    entrances=entrances,
                    spaces=spaces,
                    walls=walls,
                    paths=paths,
                    circles=elevators,
                    squares=stairs,
                    on_close=self.on_window_close
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open SVG: {e}")
    
    def on_window_close(self, window):
        if window == self.current_window:
            self.current_window = None
    
    def show_about(self):
        about_text = """
        Pather - SVG Map Annotation Tool
        
        A tool for annotating SVG maps of buildings with paths for navigation.
        
        Features:
        - Visualize floor plans
        - Generate centerline/midline paths
        - Connect doors to paths
        - Connect floors via elevators
        - Export updated SVG files
        
        Released under GNU GPL v3
        """
        messagebox.showinfo("About Pather", about_text)

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
    # Ensure all windows are properly closed
    pygame.quit()

if __name__ == "__main__":
    main()