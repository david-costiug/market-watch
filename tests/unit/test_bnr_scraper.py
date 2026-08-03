from pathlib import Path
from app.scrapers.bnr_scraper import parse_html

def test_parse_bnr_html():
    fixture_path = Path(__file__).parent.parent / "fixtures" / "bnr_eur.html"
    html = fixture_path.read_text(encoding="utf-8")

    records = parse_html(html, "EUR")

    assert len(records) == 2
    
    r1 = records[0]
    assert r1.entity.name == "Banca Transilvania"
    assert r1.entity.platform_source == "BNR"
    assert r1.rate.currency == "EUR"
    assert r1.rate.buy == 4.9200
    assert r1.rate.sell == 4.9850

    r2 = records[1]
    assert r2.entity.name == "BCR"
    assert r2.rate.buy == 4.9150
    assert r2.rate.sell == 4.9900
