from pathlib import Path
from app.scrapers.valutare_scraper import parse_html

def test_parse_valutare_html():
    fixture_path = Path(__file__).parent.parent / "fixtures" / "valutare_eur.html"
    html = fixture_path.read_text(encoding="utf-8")

    records = parse_html(html, "EUR")

    assert len(records) == 2
    
    r1 = records[0]
    assert r1.entity.name == "Casa de Schimb Lux"
    assert r1.entity.city == "Bucuresti"
    assert r1.entity.platform_source == "Valutare"
    assert r1.rate.currency == "EUR"
    assert r1.rate.buy == 4.9500
    assert r1.rate.sell == 4.9700

    r2 = records[1]
    assert r2.entity.name == "Exchange Express"
    assert r2.entity.city == "Cluj-Napoca"
    assert r2.rate.buy == 4.9450
    assert r2.rate.sell == 4.9750
