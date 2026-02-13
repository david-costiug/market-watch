from app.core.logging import logger
from app.scrapers.valutare_scraper import scrape_valutare
from app.scrapers.bnr_scraper import scrape_bnr
from app.services.pipeline_service import process_scraped_data


def run_all():
    logger.info("Pipeline started.")

    all_records = []

    for scraper in [scrape_valutare, scrape_bnr]:
        try:
            records = scraper()
            logger.info(f"Scraper {scraper.__name__} returned {len(records)} records.")
            all_records.extend(records)
        except Exception as e:
            logger.error(f"Scraper {scraper.__name__} failed: {e}")

    if not all_records:
        logger.warning("No records scraped. Pipeline will exit.")
        return

    process_scraped_data(all_records)

    logger.info("Pipeline finished.")


if __name__ == "__main__":
    run_all()
