# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 07:54:02 2024

@author: garlench
"""
import pandas as pd
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import messagebox
import mplcursors
    
class GraphWindow:
    
    def __init__(self, master, folder_path): # Initialize object instances
        
        self.folder_path = folder_path # Initialize filepath instance and make it an input in the object
        self.file_names = [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
        self.joined_path_array = [os.path.join(self.folder_path, f) for f in self.file_names]
        
        self.current_index = 0 # Intialize the current index
        self.load_csv(self.current_index)
        
        # Master window --------------------------------------------------------------------------------------------
        self.master = master
        self.master.geometry("1280x720")
        
        # PanedWindow for graph and checkbox ------------------------------------------------------------------------------------
        self.paned_window = ttk.PanedWindow(self.master, orient = 'horizontal')
        self.paned_window.pack(fill = 'both',
                               expand = True)
        
        # Frame for ScrollableFrame --------------------------------------------------------------------------------------------
        self.container_frame = ctk.CTkFrame(self.paned_window)
        self.paned_window.add(self.container_frame, weight = 1)
        
        # Scrollable Frame  --------------------------------------------------------------------------------------------
        self.frame_for_checkbox = ctk.CTkScrollableFrame(self.container_frame)
        self.frame_for_checkbox.pack(fill = 'both',
                                     expand = True)
        
        # Dictionary to store the header variables and their checkboxes
        self.header_vars = {}
        self.checkboxes = {}
        self.create_checkboxes()
        
        # Graph Frame --------------------------------------------------------------------------------------------
        self.frame_for_graph = ctk.CTkFrame(self.paned_window)
        self.paned_window.add(self.frame_for_graph, weight = 2)
        self.frame_for_graph.grid_columnconfigure(0, weight = 1)
        self.frame_for_graph.grid_columnconfigure(1, weight = 1)
        self.frame_for_graph.grid_columnconfigure(2, weight = 1)
        self.frame_for_graph.grid_rowconfigure(0, weight = 1)
        self.frame_for_graph.grid_rowconfigure(1, weight = 9)
        
        # File Combobox --------------------------------------------------------------------------------------------
        self.combobox_files = ctk.CTkOptionMenu(master = self.frame_for_graph,
                                              values = self.joined_path_array,
                                              command = self.combobox_selected)
        self.combobox_files.grid(row = 0,
                                 column = 0,
                                 columnspan = 2,
                                 sticky = 'ew',
                                 padx = 5,
                                 pady = 5)
        self.combobox_files.configure(state = 'normal',
                                      hover = True,
                                      dropdown_fg_color = 'black',
                                      fg_color = 'black',
                                      button_color = 'black')

        
        # Plot Button --------------------------------------------------------------------------------------------
        self.plot_button = ctk.CTkButton(self.frame_for_graph, 
                                         text = "Plot!", 
                                         command = self.plot_graph)
        self.plot_button.grid(row = 0,
                              column = 2,
                              sticky = 'ew',
                              padx = 5,
                              pady = 5)
        
        # Bind arrow keys to functions --------------------------------------------------------------------------------------------
        master.bind('<Right>', self.fwd_button_fn)
        master.bind('<Left>', self.bwd_button_fn)
        
        # MPL Fig and Canvas --------------------------------------------------------------------------------------------
        self.fig, self.ax = plt.subplots(figsize = (8, 4.5),
                                         dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame_for_graph)
        self.canvas.get_tk_widget().grid(row = 1,
                                         column = 0,
                                         columnspan = 3,
                                         sticky = 'nswe',
                                         padx = 5,
                                         pady = 5)

        
        # Add in the toolbar from inbuilt matplotlib graph
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                            self.frame_for_graph,
                                            pack_toolbar = False)
        self.toolbar.update()
        self.toolbar.grid(sticky = 'ew',
                          columnspan = 3,
                          padx = 5,
                          pady = 5)
        
    # Function to load .csv 
    def load_csv(self, index):
        self.df = pd.read_csv(self.joined_path_array[index])
    
    # Make Checkboxes
    def create_checkboxes(self):
        # Clear existing checkboxes
        for widget in self.frame_for_checkbox.winfo_children():
            widget.destroy()
        
        # Dictionary to store the header variables and their checkboxes
        self.header_vars = {}
        self.checkboxes = {}
        
        for i in self.df.columns.tolist()[1:]:
            self.header_vars[i] = self.df[i]
            var = ctk.StringVar(value="off")
            self.checkboxes[i] = var
            
            column_checkbox = ctk.CTkCheckBox(self.frame_for_checkbox,
                                              text=i,
                                              variable=var,
                                              onvalue = "on",
                                              offvalue = "off",
                                              border_width = 2,
                                              checkbox_width = 15,
                                              checkbox_height = 15)
            column_checkbox.pack(anchor = 'w')
        
    # Plotting function    
    def plot_graph(self):
        # Clear the current axes
        self.ax.clear()
        
        # Get only the checked items
        checked_items = [header for header, var in self.checkboxes.items() if var.get() == "on"]
        
        lines = []
        # Plot the graph for checked items
        for header in checked_items:
            line, = self.ax.plot(self.df['Time'], self.header_vars[header], label = header)
            lines.append(line)
            
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Values')
        self.ax.set_title('Graph for {}')
        self.ax.grid(True)
        
        self.ax.legend(draggable = True)
        self.cursor = mplcursors.cursor(lines,
                                        multiple = True)
        
        # Draw the updated figure
        self.canvas.draw()
        
    def fwd_button_fn(self, event=None):
        if self.current_index < len(self.joined_path_array) - 1:
            self.current_index += 1
            self.load_csv(self.current_index)
            self.create_checkboxes()
            self.plot_graph()
        else:
            messagebox.showinfo("Info", "You are at the last file.")
    
    def bwd_button_fn(self, event=None):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_csv(self.current_index)
            self.create_checkboxes()
            self.plot_graph()
        else:
            messagebox.showinfo("Info", "You are at the first file.")
            
    def combobox_selected(self, event):
        selected_file = self.combobox_files.get()
        self.current_index = self.joined_path_array.index(selected_file)
        self.load_csv(self.current_index)
        self.create_checkboxes()
        self.plot_graph()

if __name__ == '__main__':
    file_path = r"test.csv"
    root = ctk.CTk()
    GraphWindow(root, file_path)
    root.title('Grapher for Converted CSVs')
    root.mainloop()
            