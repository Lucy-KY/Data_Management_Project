from collections.abc import Set
import os, csv
from typing import Any, List, Dict
from data_warehouse import DataWarehouse


class MyDataWarehouse(DataWarehouse):
    def __init__(self, partition_size: int, storage_dir: str) -> None:
        self.partition_size = partition_size
        self.storage_dir = storage_dir
        if(not os.path.exists(storage_dir)):
            os.makedirs(storage_dir)
    
    def get_partition_path(self, id: str) -> str:
        idInt = int(id)
        partition_index = (idInt - 1) // self.partition_size
        return os.path.join(self.storage_dir, f"partition_{partition_index}.csv")
    
    def add_data(self, data: Dict[str, Any]) -> None:
        filePath = self.get_partition_path(data["id"])
        fileExist = os.path.isfile(filePath)
        with open(filePath, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldNames = list(data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldNames, extrasaction="ignore")
            # Write header only if file is new
            if (not fileExist):
                writer.writeheader()
            writer.writerow(data)
        return

    def update_data(self, key_column: str, key_value: Any, updated_data: Dict[str, Any]) -> None:
        # Range pagination based on id
        filePath = self.get_partition_path(key_value)
        update = False
        
        with open(filePath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldNames = reader.fieldnames
            rows = []
            for row in reader:
                if row.get(key_column) == str(key_value):
                    update = True
                    row.update(updated_data)
                rows.append(row)
        if update:
            with open(filePath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
                writer.writeheader()
                writer.writerows(rows)
        return

    def delete_data(self, key_column: str, key_value: Any) -> None:
        delete = False
        
        filePath = self.get_partition_path(key_value)
        #File path may not exist
        if not os.path.exists(filePath):
            return
        with open(filePath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldNames = reader.fieldnames
            rows = []
            for row in reader:
                if row[key_column] == str(key_value):
                    delete = True
                else:
                    rows.append(row)
            
        if delete:
            with open(filePath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
                writer.writeheader()
                writer.writerows(rows)
        return

    def query_data(self, key_column: str, keys: List[Any]) -> List[Dict[str, Any]]:
        if(keys is None or len(keys) == 0):
            return []
        results = []
        
        # Partition: Map<filePath, Set<key>>
        tasks: Dict[str, Set[str]] = {}
        for key in keys:
            path = self.get_partition_path(key)
            if path not in tasks:
                tasks[path] = set()
            tasks[path].add(str(key))
            
        # Query each partition
        for filePath, target in tasks.items():
            if not os.path.exists(filePath):
                continue
            with open(filePath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row[key_column] in target:
                        results.append(row)
        return results