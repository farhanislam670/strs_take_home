from pathlib import Path
from sqlalchemy.orm import Session
from src.ingestion.csv_loader import CSVLoader
from src.ingestion.data_cleaner import DataCleaner
from src.ingestion.db_writer import DatabaseWriter
from src.schemas.property_csv import CleanedPropertyData
from typing import List
import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates the entire ingestion process."""
    
    def __init__(self, session: Session, batch_size: int = 500):
        self.session = session
        self.batch_size = batch_size
        self.db_writer = DatabaseWriter(session)
        self.cleaner = DataCleaner()
    
    def ingest_csv(self, csv_path: Path, market_area: str) -> dict:
        """Ingest a single CSV file."""
        logger.info(f"Starting ingestion for {csv_path.name} (Market: {market_area})")
        
        loader = CSVLoader(csv_path, market_area, skip_errors=True)
        
        batch: List[CleanedPropertyData] = []
        total_processed = 0
        total_skipped = 0
        rows_from_loader = 0
        
        for raw_row in loader.load():
            rows_from_loader += 1
            
            # Check if row should be skipped
            should_skip, skip_reason = self.cleaner.should_skip_row(raw_row)
            if should_skip:
                logger.debug(f"Skipping property {raw_row.property_id}: {skip_reason}")
                total_skipped += 1
                continue
            
            # Clean and transform
            cleaned = self.cleaner.resolve_duplicates(raw_row, market_area)
            batch.append(cleaned)
            
            # Write in batches
            if len(batch) >= self.batch_size:
                logger.info(f"📦 Writing batch of {len(batch)} properties...")
                count = self.db_writer.upsert_properties(batch)
                total_processed += count
                batch = []
                logger.info(f"Processed {total_processed} properties so far...")
        
        # Log before final batch
        logger.info(f"Loop finished. Received {rows_from_loader} rows from loader. Remaining batch size: {len(batch)}")
        
        # Write remaining batch
        if batch:
            logger.info(f"📦 Writing final batch of {len(batch)} properties...")
            count = self.db_writer.upsert_properties(batch)
            total_processed += count
            logger.info(f"Final batch wrote {count} properties")
        
        logger.info(
            f"✅ Completed {csv_path.name}: "
            f"{total_processed} properties ingested, "
            f"{total_skipped} skipped"
        )
        
        return {
            'ingested': total_processed,
            'skipped': total_skipped
        }
    
    def ingest_all(self, data_dir: Path) -> dict:
        """
        Discover and ingest all CSV files in directory.
        
        Returns:
            Summary dict with stats per market
        """
        csv_files = CSVLoader.discover_csv_files(data_dir)
        
        if not csv_files:
            logger.warning(f"No CSV files found in {data_dir}")
            return {}
        
        results = {}
        
        for csv_path, market_area in csv_files:
            try:
                stats = self.ingest_csv(csv_path, market_area)
                results[market_area] = {
                    'status': 'success',
                    **stats
                }
            except Exception as e:
                logger.error(f"Failed to ingest {csv_path.name}: {e}", exc_info=True)
                results[market_area] = {
                    'status': 'failed',
                    'ingested': 0,
                    'skipped': 0,
                    'error': str(e)
                }
        
        return results