"""
Created on Sat Nov 23 14:24:11 2024

@author: garlench
"""

"""
Goal: Utilize OOP to create an app that:
    - centralizes data analysis for toolset
    - browse for folders with data required for analysis
    - add optional method for graphing files in the directory
    
User Input = folder file path
- schematic:
    - folder_path > FolderRead > Qual > Qual.function(parameters)
"""

import pandas as pd 
import os 
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
import RecToGraph as rtg


# Take in the file directory and parse the rec files
def FolderRead(folder_path):
    folder_path = os.path.abspath(folder_path) # Turn the filepath into an absolute path
    file_names = os.listdir(folder_path) # Get the list of files in the directory
    
    dataframe_collection = [] # Initialize empty array to collect dataframes
    csv_filepath_collection = [] # Initialize empty array to collect .csv filepaths
    
    for filename in file_names: # For each file in the directory
        if filename.endswith('.rec'): # If it is a rec file then execute the algorithm
            with open(os.path.join(folder_path, filename), 'r') as file:
                lines = file.readlines()
                
                # Find the start of the header version and data sections
                header_start = lines.index('[Header]\n') + 1  # Skip the '[Header]' line
                data_start = lines.index('[Data]\n') + 1  # Skip the '[Data]' line
                
                # Read the headers
                headers_line = lines[header_start].strip()
                headers = headers_line.split("' '")
                
                # Remove the leading and trailing single quotes from the first and last header
                headers[0] = headers[0][1:]
                headers[-1] = headers[-1][:-1]
                
                # Read the data
                data = [line.strip().split(' ') for line in lines[data_start:] if line.strip()]
                
                # Create a DataFrame
                df = pd.DataFrame(data, columns = headers)
                df.to_csv(os.path.join(folder_path, os.path.splitext(filename)[0]) + ".csv", index = False)
                dataframe_collection.append(df)
                csv_filepath_collection.append(os.path.join(folder_path, os.path.splitext(filename)[0]) + ".csv")
        
    return csv_filepath_collection

class Qual:
    def __init__(self, csv_list):
        """
        Parameters
        ----------
        csv_list : str (filepath)
            filepath instance required to initialize

        Returns
        -------
        None.
        """
        self.csv_list = csv_list
        self.directory_name = os.path.dirname(csv_list[0]) 

#%% Qual functions    
    def Analysis(self, Tool, FU, Power):
        """
        Parameters
        ----------
        Tool : str
            requests input of specific device for analysis.
        FU : int
            tool parameter.
        Power : float
            tool parameter.

        Returns
        -------
        None.
        """
        results_df = pd.DataFrame() # Initialize empty dataframe to collect results
        
        for csv_file in self.csv_list: # For each csv in the csv file list 
            df = pd.read_csv(csv_file) 
            # df_headers = df.columns.tolist() #get headers in the file
            
            #collect the stats of the file
            stats_dict = {
                # 'SUBSTRATE ID': df['Substrate ID'].iloc[0],
                'TOOL': Tool,
                'FU': FU,
                'POWER': Power,
                'Force Max 1 [N]': df['Force1'].max(),
                'Force Max 2 [N]': df['Force2'].max(),
                'Force Max 3 [N]': df['Force3'].max(),
                'Force Max Cumulative': df['ForceCumulative'].max(),
                'Force Min 1 [N]': df['Force1'].min(),
                'Force Min 2 [N]': df['Force2'].min(),
                'Force Min 3 [N]': df['Force3'].min(),
                'Force Min Cumulative [N]': df['ForceCumulative'].min()
                }
            
            stats_df = pd.DataFrame([stats_dict]) #build stats into df

            stats_df['Lowest Force'] = stats_df[['Force Min 1 [N]', 
                                         'Force Min 2 [N]',
                                         'Force Min 3 [N]']].min(axis = 1)
            
            results_df = pd.concat([results_df, stats_df], ignore_index=True)
            
        results_df.to_excel(os.path.join(self.directory_name, "Analysis Forces.xlsx"), index = False)
        os.system('start EXCEL.EXE "{}"'.format(os.path.join(self.directory_name, "Analysis Forces.xlsx")))


#%% Custom Tkinter GUI -------------------------
class MainApp: # Main Window Object
    
    def __init__(self, master): # Initialize object attributes
        self.master = master # Master attribute - it is root

        self.master.geometry('1280x720')
        self.master.configure(bg = "#C4DCE4")
        # self.master.grid_columnconfigure(0, weight = 1)
        self.master.grid_columnconfigure(0, weight = 1)
        self.master.grid_columnconfigure(1, weight = 1)
        self.master.grid_columnconfigure(2, weight = 1)
        self.master.grid_rowconfigure(7, weight = 1)
        
        how_to_use = """
        Welcome!
        
        This is an app created to centralize engineering data analysis for the toolsets. 
        Please:
            • Click Browse to select a folder with all your .rec files
            • Click "Initialize"
            • Select the proper tool
            • Select the target module
            • Click the appropriate module to run the analysis! Once analyzed, the .xlsx file will open.
            • Repeat the flow for any other folders you would like to analyze
            • Click the "Graph .csv Files" button to graph the items in the directory
            
        Contact me with any issues.
        FYI - This application is a sample app with obfuscated data.
        """
        
        # Main text ------------------------------------------------------------------------------------
        self.main_text = ctk.CTkLabel(master, # Main Window Label
                              text = how_to_use,
                              font = ctk.CTkFont(size = 14, family = "Arial"),
                              justify = "left"
                              ) 
        self.main_text.grid(row = 0,
                            column = 0,
                            columnspan = 3,
                            sticky = 'ew')
        
        # Browse Button ------------------------------------------------------------------------------------
        self.browse_button = ctk.CTkButton(master, # Browse button object attribute
                                text = "Browse...", 
                                command = self.browse_for_filepath)
        self.browse_button.grid(row = 1,
                            column = 2,
                            sticky = 'w')
        
        # Filepath Box ------------------------------------------------------------------------------------
        self.file_path_box = ctk.CTkTextbox(master,
                                            font = ctk.CTkFont(size = 12, family="Arial"), # File path box object attribute
                                            height = 30)
        self.file_path_box.grid(row = 1,
                            column = 1,
                            sticky = 'ew',
                            pady = 5)
        self.file_path_box.configure(state = "disabled")
        
        # Graph button ------------------------------------------------------------------------------------
        self.graph_button = ctk.CTkButton(self.master, # Graph Button Attribute
                                    text = "Graph .csv Files",
                                    command = self.graph_subwindow_init)
        self.graph_button.grid(row = 2,
                            column = 1,
                            pady = 5)
         
        # Initialize button ------------------------------------------------------------------------------------
        self.initialize_button = ctk.CTkButton(master, # Initialize button object attribute
                                   text = "Initialize", 
                                   command = self.initialize_button_analysis)
        self.initialize_button.grid(row = 3,
                                    column = 1,
                                    pady = 5)
        
        self.file_path = ""  # Initialize file_path as an empty string

        # Credit line ------------------------------------------------------------------------------------        
        self.garlen_credit = ctk.CTkLabel(master, # Credit Text
                              text = "Created by Garlen Chan",
                              font = ctk.CTkFont(size = 12, family = "Arial"),
                              justify = "left")
        self.garlen_credit.grid(row = 7,
                                column = 1,
                                sticky = 's')

        # Functions ------------------------------------------------------------------------------------
    def browse_for_filepath(self): # Class Function

        filename = filedialog.askdirectory() # Ask for the rec file directory
        self.file_path_box.configure(state = "normal")
        self.file_path_box.delete("1.0", "end")
        self.file_path_box.insert("end", filename)
        self.file_path_box.configure(state = "disabled")
        
    def initialize_button_analysis(self):
        self.file_path = self.file_path_box.get("1.0", 'end-1c')  # Get the text from the file_path_box
        
        if self.file_path != "":
            self.Tool_button = ctk.CTkButton(self.master,
                                        text = "Tool",
                                        command = self.Tool_button_subentity)
            self.Tool_button.grid(row = 4,
                                   column = 1,
                                   padx = 5,
                                   pady = 5,
                                   sticky = 'n')
            
        else:
            messagebox.showerror("Error", "Please don't leave the filepath box blank.")
    
    def graph_subwindow_init(self):
        
        try:
            self.file_path = self.file_path_box.get("1.0", "end-1c")
            FolderRead(self.file_path)
            root = ctk.CTk()
            rtg.GraphWindow(root, self.file_path)
            root.title('Grapher for Converted CSVs')
            root.mainloop()
            
        except Exception as e:
            if self.file_path == "":
                messagebox.showerror("Error", "Please select a valid filepath.")
                root.destroy()
            else:
                messagebox.showerror("Error", f"{e}\nThere are no .csv files here, or they do not originate from .rec files.\nPlease parse the .rec files first before using this utility.")
                root.destroy()
        
    def Tool_button_subentity(self):
        
        try:
            modules = ['Analysis']
            column_positions = [1]
            stickies = ['n']
            
            def create_command(func):
                return lambda: self.safe_execute(func)
            
            qual_functions = [
                create_command(lambda: Qual(FolderRead(r"{}".format(self.file_path_box.get("1.0", "end-1c")))).Analysis("TEST", "TEST", "TEST"))
            ]  

            for i, modules in enumerate(modules):
                self.module_button = ctk.CTkButton(self.master,
                                            text = "{}".format(modules),
                                            command = qual_functions[i])
                self.module_button.grid(row = 5,
                                        column = column_positions[i],
                                        pady = 5,
                                        sticky = stickies[i])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}\n Please select a filepath.")
            
    def safe_execute(self, func):
        try:
            func()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}\nDid you select the right module?")

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApp(root)
    root.title('Rec File Analysis')
    root.mainloop()