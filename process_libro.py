import openpyxl
import json
import os

def get_code_from_value(value, code_map):
    """
    Searches for a value in the codebook and returns its corresponding code.
    It checks both categories and combinations.
    """
    if value is None:
        return None

    str_value = str(value).strip().lower()

    # Check in categories
    for code, text in code_map.get("categories", {}).items():
        if str(text).strip().lower() == str_value:
            return int(code)

    # Check in combinations
    for code, text in code_map.get("combinations", {}).items():
        if str(text).strip().lower() == str_value:
            return int(code)
    
    return value

def main():
    # 1. Read Libro1.xlsx (now with headers)
    excel_file = 'Libro1.xlsx'
    try:
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
        
        data = []
        headers = [cell.value for cell in sheet[1]]
        
        # Iterate starting from row 2
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Check if row is empty
            if all(cell is None for cell in row):
                continue
            data.append(dict(zip(headers, row)))
            
        print(f"Loaded {len(data)} rows from {excel_file}")
        
    except FileNotFoundError:
        print(f"Error: {excel_file} not found.")
        return

    # 2. Load the codebook
    try:
        with open('libro_codigos.json', 'r', encoding='utf-8') as f:
            codebook = json.load(f)
    except FileNotFoundError:
         print("Error: libro_codigos.json not found.")
         return

    # 3. Create a mapping from question label to codebook key
    label_to_key = {details['label']: key for key, details in codebook.items()}

    # 4. Process and codify the data
    coded_data = []
    for entry in data:
        coded_entry = {}
        for key, value in entry.items():
            if key in label_to_key:
                codebook_key = label_to_key[key]
                code_map = codebook[codebook_key]
                coded_value = get_code_from_value(value, code_map)
                coded_entry[key] = coded_value
            else:
                coded_entry[key] = value
        coded_data.append(coded_entry)

    # 5. Save the coded data to 'kobo_data_export_code.json'
    output_filename = 'kobo_data_export_code.json'
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(coded_data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully processed and saved coded data to {output_filename}")

if __name__ == "__main__":
    main()