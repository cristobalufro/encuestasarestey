import requests
import pandas as pd
import json
import re

# --- Hardcoded credentials ---
API_TOKEN = 'e847b97761bf2a4e167cd24b1463eb17f23df543'
ASSET_UID = 'aDnccWUpBGWE9qbNhDZRTb'
# ---------------------------

def fetch_form_structure():
    """Fetches the form structure to get question labels and choice names."""
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{ASSET_UID}.json"
    headers = {"Authorization": f"Token {API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Decode the response content manually to ensure correct UTF-8 handling
        response_text = response.content.decode('utf-8')
        form_data = json.loads(response_text)
        
        content = form_data.get("content", {})
        
        # Parse choices
        choice_lookup = {}
        for choice_list in content.get("choices", []):
            for choice in choice_list.get("choices", []):
                choice_lookup[choice["name"]] = choice["label"][0]

        # Parse survey questions recursively
        name_to_label = {}
        if "survey" in content:
            process_survey_elements(content["survey"], name_to_label)
            
        return name_to_label, choice_lookup

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch form structure: {e}")
        return None, None
    except (KeyError, IndexError) as e:
        print(f"Error: Failed to parse form structure: {e}")
        return None, None

def process_survey_elements(elements, name_to_label):
    """Recursively processes survey elements to map question names to labels."""
    for elem in elements:
        if elem.get('type') in ['begin_group', 'begin_repeat'] and 'children' in elem:
            process_survey_elements(elem['children'], name_to_label)
        
        name = elem.get('$autoname') or elem.get('name')
        label_list = elem.get('label')
        if name and label_list:
            name_to_label[name] = label_list[0]

def fetch_data():
    """Fetches the submission data from the KoboToolbox API."""
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{ASSET_UID}/data.json"
    headers = {"Authorization": f"Token {API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Decode the response content manually
        response_text = response.content.decode('utf-8')
        data = json.loads(response_text)
        
        return pd.DataFrame(data.get("results", []))
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch data: {e}")
        return None

def translate_dataframe(df, name_to_label, choice_lookup):
    """Translates column names and values to human-readable format."""
    if df is None or df.empty:
        return pd.DataFrame()

    translatable_columns = {}
    for col in df.columns:
        simple_name = col.split('/')[-1]
        if simple_name in name_to_label:
            translatable_columns[col] = name_to_label[simple_name]
    
    translated_df = df[list(translatable_columns.keys())].copy()
    
    def translate_value(x):
        if isinstance(x, str):
            # Explicitly handle potential encoding issues
            try:
                x = x.encode('latin1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass # Keep original string if conversion fails

            parts = re.split(r'[ _]', x)
            translated_parts = [choice_lookup.get(part, part) for part in parts]
            return ', '.join(translated_parts)
        return choice_lookup.get(x, x)

    for col_name in translated_df.columns:
        translated_df.loc[:, col_name] = translated_df[col_name].apply(translate_value)

    translated_df.rename(columns=translatable_columns, inplace=True)
    return translated_df

def main():
    """Main function to fetch, process, and export data."""
    print("Fetching form structure...")
    name_to_label, choice_lookup = fetch_form_structure()
    
    if name_to_label is None or choice_lookup is None:
        print("Could not proceed without form structure. Exiting.")
        return

    print("Fetching data...")
    df = fetch_data()
    
    if df is None:
        print("Could not proceed without data. Exiting.")
        return

    print("Translating data...")
    translated_df = translate_dataframe(df, name_to_label, choice_lookup)
    
    output_filename = 'kobo_data_export.xlsx'
    print(f"Saving data to {output_filename}...")
    
    try:
        translated_df.to_excel(output_filename, index=False, engine='openpyxl')
        print("Export successful!")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        print("Please make sure you have 'openpyxl' installed (`pip install openpyxl`).")

if __name__ == "__main__":
    main()