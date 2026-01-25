import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import SessionLocal
from src.ingestion.pipeline import IngestionPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the ingestion pipeline."""
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Starting STRSeach Data Ingestion Pipeline")
    logger.info("=" * 60)
    
    session = SessionLocal()
    
    try:
        pipeline = IngestionPipeline(session, batch_size=500)
        
        # # singluar csv file
        # csv_path = data_dir / "Indianapolis IN.csv"
        # # ingest_csv returns a dict with 'ingested' and 'skipped' keys
        # stats = pipeline.ingest_csv(csv_path, market_area="Indianapolis")

        # ingest all csv files
        stats = pipeline.ingest_all(data_dir)
        for market_area, stats in stats.items():
            logger.info(f"✅ {market_area}: {stats['ingested']} ingested, {stats['skipped']} skipped")
            logger.info(f"Stats: {stats}")

        logger.info("=" * 60)
        logger.info("Ingestion Complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()