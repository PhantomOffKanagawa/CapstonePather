import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import threading
from svg_parser import parse_svg
from display import MapWindow, init_pygame
from values import *

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Pather - SVG Map Annotation Tool")
        self.root.geometry("500x300")
        
        self.open_windows = []
        
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
        init_pygame()
        
        # Check for output directory
        os.makedirs("./output", exist_ok=True)
        
        # Set up a periodic check for window closures
        self.check_windows()
        
    def open_svg(self):
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
                width, height, entrances, spaces, walls, paths = parse_svg(file_path)
                
                # Create a new map window in a separate thread to keep the main window responsive
                thread = threading.Thread(
                    target=self.create_map_window,
                    args=(file_path, map_name, width, height, entrances, spaces, walls, paths)
                )
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open SVG: {e}")
    
    def create_map_window(self, file_path, map_name, width, height, entrances, spaces, walls, paths):
        # Create a new map window
        map_window = MapWindow(
            file_path=file_path,
            map_name=map_name,
            width=width,
            height=height,
            entrances=entrances,
            spaces=spaces,
            walls=walls,
            paths=paths,
            elevators=[],
            stairs=[],
            on_close=self.on_window_close
        )
        
        self.open_windows.append(map_window)
    
    def on_window_close(self, window):
        if window in self.open_windows:
            self.open_windows.remove(window)
    
    def check_windows(self):
        """Periodically check if any windows were closed externally and update the list"""
        # Filter out windows that are no longer running
        self.open_windows = [w for w in self.open_windows if w.running]
        
        # Schedule the next check
        self.root.after(1000, self.check_windows)
    
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