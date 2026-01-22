import csv
import os
from typing import Any, List, Dict
from data_warehouse import DataWarehouse


class NaiveCSVWarehouse(DataWarehouse):
    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        
    def add_data(self, data: Dict[str, Any]) -> None:
        # Header initialization
        self.fieldNames = list(data.keys())
        fileExist = os.path.isfile(self.csv_path)
        with open(self.csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames, extrasaction="ignore")
            # Write header only if file is new
            if (not fileExist):
                writer.writeheader()
            writer.writerow(data)
        return

    def update_data(self, key_column: str, key_value: Any, updated_data: Dict[str, Any]) -> None:
        update = False
        with open(self.csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldNames = reader.fieldnames
            rows = []
            for row in reader:
                if row.get(key_column) == str(key_value):
                    update = True
                    row.update(updated_data)
                rows.append(row)
        if update:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
                writer.writeheader()
                writer.writerows(rows)
        return

    def delete_data(self, key_column: str, key_value: Any) -> None:
        # Implementation here
        delete = False
        with open(self.csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldNames = reader.fieldnames
            rows = []
            for row in reader:
                if row[key_column] == str(key_value):
                    delete = True
                else:
                    rows.append(row)

        if delete:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
                writer.writeheader()
                writer.writerows(rows)
        return

    def query_data(self, key_column: str, keys: List[Any]) -> List[Dict[str, Any]]:
        # Implementation here
        if(keys is None or len(keys) == 0):
            return []
        strKey = {str(key) for key in keys}
        results = []
        with open(self.csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row[key_column] in strKey:
                    results.append(row)
        return results
