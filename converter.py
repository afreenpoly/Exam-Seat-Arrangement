import json
import pandas as pd


def excel_to_json(excel_file):
    # Load the Excel file into a Pandas DataFrame
    df = pd.read_excel(excel_file)

    # Convert the DataFrame to a JSON string
    json_str = df.to_json(orient='records')

    # Load the JSON string into a Python dictionary
    data = json.loads(json_str)
    # Return the dictionary

    return data
