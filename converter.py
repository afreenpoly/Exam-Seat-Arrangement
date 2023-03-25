import json
import pandas as pd


def excel_to_json(excel_file):
    # Load the Excel file into a Pandas DataFrame
    excel_data = pd.read_excel(excel_file, sheet_name=None)

    json_data = {}
    for sheet_name, sheet_data in excel_data.items():
        json_data[sheet_name] = json.loads(sheet_data.to_json(orient='records'))
    return json_data
