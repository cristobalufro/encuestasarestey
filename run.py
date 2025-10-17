import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests
import pandas as pd
import json
import re

# --- Hardcoded credentials ---
API_TOKEN = 'e847b97761bf2a4e167cd24b1463eb17f23df543'
ASSET_UID = 'aDnccWUpBGWE9qbNhDZRTb'
# ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KoboToolbox Data Viewer")
        self.geometry("1024x768")

        self.api_token = API_TOKEN
        self.asset_uid = ASSET_UID
        self.name_to_label = {}
        self.choice_lookup = {}

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a frame for the Treeview and scrollbars
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create the Treeview widget
        self.tree = ttk.Treeview(tree_frame)

        # Create vertical and horizontal scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout for the Treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure the grid to expand
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.setup_menu()

    def setup_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

    def get_user_inputs(self):
        # Hardcoded values are used, so we just confirm they exist.
        return self.api_token and self.asset_uid

    def fetch_form_structure(self):
        if not self.api_token or not self.asset_uid:
            return

        url = f"https://kf.kobotoolbox.org/api/v2/assets/{self.asset_uid}.json"
        headers = {"Authorization": f"Token {self.api_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Decode the response content manually to ensure correct UTF-8 handling
            response_text = response.content.decode('utf-8')
            form_data = json.loads(response_text)
            content = form_data.get("content", {})
            
            # Parse choices
            self.choice_lookup = {}
            for choice_list in content.get("choices", []):
                for choice in choice_list.get("choices", []):
                    self.choice_lookup[choice["name"]] = choice["label"][0]

            # Parse survey questions recursively
            self.name_to_label = {}
            if "survey" in content:
                self.process_survey_elements(content["survey"])

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch form structure: {e}")
        except (KeyError, IndexError) as e:
            messagebox.showerror("Error", f"Failed to parse form structure: {e}")

    def process_survey_elements(self, elements):
        for elem in elements:
            if elem.get('type') in ['begin_group', 'begin_repeat'] and 'children' in elem:
                self.process_survey_elements(elem['children'])
            
            name = elem.get('$autoname') or elem.get('name')
            label_list = elem.get('label')
            if name and label_list:
                self.name_to_label[name] = label_list[0]

    def fetch_data(self):
        if not self.api_token or not self.asset_uid:
            return None

        url = f"https://kf.kobotoolbox.org/api/v2/assets/{self.asset_uid}/data.json"
        headers = {"Authorization": f"Token {self.api_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Decode the response content manually to ensure correct UTF-8 handling
            response_text = response.content.decode('utf-8')
            data = json.loads(response_text)
            return pd.DataFrame(data.get("results", []))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")
            return None

    def translate_dataframe(self, df):
        if df is None or df.empty:
            return pd.DataFrame()

        # Get the columns that exist in both the DataFrame and the name_to_label mapping
        # Match columns by checking if the simple name (after the last '/') is in the mapping
        translatable_columns = {}
        for col in df.columns:
            simple_name = col.split('/')[-1]
            if simple_name in self.name_to_label:
                translatable_columns[col] = self.name_to_label[simple_name]
        
        # Create a new DataFrame with only the translatable columns
        translated_df = df[list(translatable_columns.keys())].copy()
        
        # Define the translation function
        import re
        def translate_value(x):
            if isinstance(x, str):
                # Handle space or underscore-separated values for select_multiple
                parts = re.split(r'[ _]', x)
                translated_parts = [self.choice_lookup.get(part, part) for part in parts]
                return ', '.join(translated_parts) # Join with comma and space for readability
            # Handle other types (numbers, etc.)
            return self.choice_lookup.get(x, x)

        # Translate values in each column BEFORE renaming the columns
        for col_name in translated_df.columns:
            # Use .loc to ensure we are modifying the DataFrame directly
            translated_df.loc[:, col_name] = translated_df[col_name].apply(translate_value)

        # Now, rename the columns to their human-readable labels
        translated_df.rename(columns=translatable_columns, inplace=True)

        return translated_df

    def display_data(self, df):
        # Clear previous data
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = []

        if df is None or df.empty:
            return

        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W)

        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def load_data(self):
        # Re-enabled manual loading to diagnose the issue
        if self.get_user_inputs():
            self.fetch_form_structure()
            df = self.fetch_data()
            translated_df = self.translate_dataframe(df)
            self.display_data(translated_df)

if __name__ == "__main__":
    app = App()
    # Removed automatic data loading to allow for manual trigger
    app.mainloop()