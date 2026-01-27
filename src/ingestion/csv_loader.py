import pandas as pd
from pathlib import Path
from typing import List, Iterator
from src.schemas.property_csv import PropertyCSVRow
import logging
import math

logger = logging.getLogger(__name__)


class CSVLoader:
    """Loads and validates CSV files."""
    
    def __init__(self, csv_path: Path, market_area: str, skip_errors: bool = True):
        self.csv_path = csv_path
        self.market_area = market_area
        self.skip_errors = skip_errors
    
    @staticmethod
    def _has_error_reason(value) -> bool:
        """
        Check if error_reason value is meaningful (not null/empty).
        
        Handles various null representations: None, NaN, empty string, "None", etc.
        """
        if value is None:
            return False
        
        # Check for NaN (float)
        if isinstance(value, float) and math.isnan(value):
            return False
        
        # Convert to string and check
        str_value = str(value).strip()
        
        # Check for empty or common null representations
        if not str_value or str_value.lower() in ('none', 'nan', 'null', ''):
            return False
        
        return True
        
    def load(self) -> Iterator[PropertyCSVRow]:
        """
        Load CSV and yield validated rows.
        
        Yields:
            PropertyCSVRow objects that passed Pydantic validation
        """
        logger.info(f"Loading CSV: {self.csv_path} for market: {self.market_area}")
        
        df = pd.read_csv(self.csv_path, low_memory=False)
        
        logger.info(f"Loaded {len(df)} rows from {self.csv_path.name}")
        
        skipped_with_errors = 0
        validation_failures = 0
        yielded = 0
        
        # Yield validated rows
        for idx, row in df.iterrows():
            try:
                # Convert row to dict, keeping NaN as is
                row_dict = row.to_dict()
                
                # Skip rows with error_reason if enabled
                if self.skip_errors:
                    error_reason = row_dict.get('error_reason')
                    
                    if self._has_error_reason(error_reason):
                        logger.debug(
                            f"Skipping row {idx} (property: {row_dict.get('Property ID', 'unknown')}) "
                            f"due to error_reason: {error_reason}"
                        )
                        skipped_with_errors += 1
                        continue
                
                # Replace NaN with None for Pydantic
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                
                validated_row = PropertyCSVRow(**row_dict)
                yielded += 1
                yield validated_row
                
            except Exception as e:
                logger.warning(
                    f"Row {idx} validation failed in {self.csv_path.name}: {e}"
                )
                validation_failures += 1
                # Continue processing other rows
                continue
        
        # Log summary
        logger.info(
            f"CSV processing summary for {self.csv_path.name}: "
            f"{yielded} rows yielded, "
            f"{skipped_with_errors} skipped (error_reason), "
            f"{validation_failures} validation failures"
        )
    
    @staticmethod
    def discover_csv_files(data_dir: Path) -> List[tuple[Path, str]]:
        """
        Discover all CSV files in data directory and infer market area.
        
        Returns:
            List of (csv_path, market_area) tuples
        """
        csv_files = []
        
        for csv_file in data_dir.glob("*.csv"):
            # Infer market area from part before first hyphen
            market_area = csv_file.stem.split("-", 1)[0].strip()
            csv_files.append((csv_file, market_area))
            
        logger.info(f"Discovered {len(csv_files)} CSV files: {[f[1] for f in csv_files]}")
        return csv_files