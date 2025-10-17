import openpyxl
import json
import argparse

def excel_to_json(excel_file, json_file):
    """
    Converts an Excel file to a JSON file.

    Args:
        excel_file (str): The path to the input Excel file.
        json_file (str): The path to the output JSON file.
    """
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook.active

    data = []
    headers = [cell.value for cell in sheet[1]]

    for row in sheet.iter_rows(min_row=2, values_only=True):
        data.append(dict(zip(headers, row)))

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Excel file to JSON file.')
    parser.add_argument('excel_file', help='The path to the input Excel file.')
    parser.add_argument('json_file', help='The path to the output JSON file.')
    args = parser.parse_args()

    excel_to_json(args.excel_file, args.json_file)
    print(f"Conversion from '{args.excel_file}' to '{args.json_file}' is complete.")