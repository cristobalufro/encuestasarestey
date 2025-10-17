import json

def get_code_from_value(value, code_map):
    """
    Searches for a value in the codebook and returns its corresponding code.
    It checks both categories and combinations.
    """
    if value is None:
        return None

    # Check in categories
    for code, text in code_map.get("categories", {}).items():
        if text == value:
            return int(code)

    # Check in combinations
    for code, text in code_map.get("combinations", {}).items():
        if text == value:
            return int(code)
    
    return value

def main():
    # Load the codebook
    with open('libro_codigos.json', 'r', encoding='utf-8') as f:
        codebook = json.load(f)

    # Load the original data
    with open('kobo_data_export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create a mapping from question label to codebook key
    label_to_key = {details['label']: key for key, details in codebook.items()}

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

    # Save the coded data to a new file
    with open('kobo_data_export_coded.json', 'w', encoding='utf-8') as f:
        json.dump(coded_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()