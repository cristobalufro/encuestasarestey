import json
from thefuzz import process
import unicodedata

def normalize_text(text):
    """
    Normalizes text by converting to lowercase, stripping whitespace,
    and removing accents.
    """
    if not isinstance(text, str):
        return text
    # NFD normalization splits characters from their accents
    # We can then filter out the accent characters (non-spacing marks)
    nfkd_form = unicodedata.normalize('NFD', text.lower().strip())
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def find_best_match(value, choices):
    """
    Finds the best match for a string from a list of choices using fuzzy matching.
    Returns the best match and its score.
    """
    best_match, score = process.extractOne(value, choices)
    return best_match, score

def transform_kobo_data(kobo_data_path, libro_codigos_path, output_path):
    """
    Transforms string values in the Kobo data export to their corresponding numeric codes
    based on the provided codebook, using fuzzy matching and text normalization.
    """
    with open(libro_codigos_path, 'r', encoding='utf-8') as f:
        libro_codigos = json.load(f)

    with open(kobo_data_path, 'r', encoding='utf-8') as f:
        kobo_data = json.load(f)

    # Create a normalized mapping from question labels to variable names
    label_to_variable_map = {normalize_text(details['label']): var_name for var_name, details in libro_codigos.items()}

    # Create forward and reverse mappings for all variables
    forward_maps = {}
    for var_name, details in libro_codigos.items():
        forward_maps[var_name] = {}
        # Add categories and combinations
        options = {**details.get('categories', {}), **details.get('combinations', {})}
        for code, text in options.items():
            forward_maps[var_name][normalize_text(text)] = code

    # Process each entry in the Kobo data
    for entry in kobo_data:
        for question_label in list(entry.keys()):
            # Handle the specific case of the alimentation question
            if "como calificaria su alimentacion?" in normalize_text(question_label):
                variable_name = "calificacion_alimentacion"
            else:
                normalized_label = normalize_text(question_label)
                variable_name = label_to_variable_map.get(normalized_label)
            
            if not variable_name:
                continue

            original_value = entry[question_label]

            if isinstance(original_value, (int, float)) or original_value is None:
                continue

            normalized_value = normalize_text(original_value)
            
            possible_choices = list(forward_maps[variable_name].keys())
            if not possible_choices:
                continue

            # Find the best match for the answer
            best_match, score = find_best_match(normalized_value, possible_choices)

            if score > 80:
                code = forward_maps[variable_name][best_match]
                entry[question_label] = int(code)
            else:
                print(f"Low confidence match for '{original_value}' -> '{best_match}' ({score}). Keeping original.")

    # Write the transformed data to the specified output file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kobo_data, f, indent=4, ensure_ascii=False)
    
    return output_path

if __name__ == "__main__":
    kobo_data_file = "kobo_data_export.json"
    libro_codigos_file = "libro_codigos.json"
    output_file = "kobo_data_export_coded.json"
    new_file = transform_kobo_data(kobo_data_file, libro_codigos_file, output_file)
    print(f"Data from {kobo_data_file} has been transformed and saved to {new_file}.")