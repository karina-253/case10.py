import csv
import json
import os.path


def read_csv_file(filename: str) -> list:
    data = []

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            read_csv = csv.DictReader(file)

            for row in read_csv:
                amount = float(row.get('amount', 0))
                transact_type = "доход" if amount >= 0 else "расход"

                transaction = {
                    'date': row.get('date', '').strip(),
                    'amount': amount,
                    'description': row.get('description', '').strip(),
                    'type': transact_type
                }
                data.append(transaction)

            return data

    except FileNotFoundError:
        print("Error: The CSV file could not be found.")
        return []


def read_json_file(filename: str) -> list:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            read_json = json.load(file)

            transactions = read_json.get('transactions', [])
            single_format = []

            for operation in transactions:
                amount = float(operation.get('amount', 0))
                transact_type = "доход" if amount >= 0 else "расход"

                transaction = {
                    'date': operation.get('date', '').strip(),
                    'amount': amount,
                    'description': operation.get('description', '').strip(),
                    'category': transact_type
                }
                single_format.append(transaction)

            return single_format

    except FileNotFoundError:
        print("Error: The JSON file could not be found.")
        return []


def import_financial_data(filename: str):
    file_type = os.path.splitext(filename)[1].lower()

    if file_type == '.csv':
        result = read_csv_file(filename)
    elif file_type == '.json':
        result = read_json_file(filename)
    else:
        print(f"Error: Unsupported file format")
        return []
    return result


data_csv = import_financial_data('money.csv')
data_json = import_financial_data('transactions.json')

print(json.dumps(data_csv, ensure_ascii=False, indent=2))
print(json.dumps(data_json, ensure_ascii=False, indent=2))
