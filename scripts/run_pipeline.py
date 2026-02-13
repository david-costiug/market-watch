from app.scrapers.valutare_scraper import scrape_valutare
from app.scrapers.bnr_scraper import scrape_bnr
from app.services.pipeline_service import process_scraped_data


def run_all():
    all_data = []

    for scraper in [scrape_valutare, scrape_bnr]:
        try:
            data = scraper()
            all_data.extend(data)
        except Exception as e:
            print(f"Scraper failed: {e}")

    process_scraped_data(all_data)


if __name__ == "__main__":
    run_all()
