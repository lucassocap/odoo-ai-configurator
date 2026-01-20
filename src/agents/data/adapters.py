"""
Data Source Adapters
Handles reading raw data from various sources (CSV, SQL, APIs)
"""
import csv
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class DataSourceAdapter(ABC):
    """Abstract base class for data source adapters"""
    
    @abstractmethod
    def read(self, source_path: str) -> List[Dict[str, Any]]:
        """Read data from source and return list of dicts"""
        pass
    
    @abstractmethod
    def validate_source(self, source_path: str) -> bool:
        """Check if source exists and is valid"""
        pass

class CSVAdapter(DataSourceAdapter):
    """Adapter for reading CSV files"""
    
    def validate_source(self, source_path: str) -> bool:
        return os.path.exists(source_path) and source_path.lower().endswith('.csv')
    
    def read(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Read CSV file and return list of records.
        Assumes first row is header.
        """
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"Invalid or missing CSV file: {source_path}")
            
        data = []
        try:
            with open(source_path, 'r', encoding='utf-8-sig') as f:
                # Use DictReader to automatically map headers
                reader = csv.DictReader(f)
                for row in reader:
                    # Clean up keys and values
                    clean_row = {
                        k.strip() if k else 'unknown': v.strip() if v else ''
                        for k, v in row.items()
                        if k # Skip empty keys
                    }
                    data.append(clean_row)
        except Exception as e:
            raise RuntimeError(f"Error reading CSV {source_path}: {e}")
            
        return data
