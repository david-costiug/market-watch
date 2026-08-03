from unittest.mock import MagicMock, patch
from app.models.exchange_rate import ExchangeRate
from app.services.validation_service import validate_rate

def test_validate_rate_no_baseline():
    conn = MagicMock()
    with patch("app.services.validation_service.get_latest_rate_for_entity", return_value=None):
        rate = ExchangeRate(currency="EUR", buy=5.0, sell=5.0, timestamp="2026-08-01T00:00:00Z")
        assert validate_rate(conn, 1, rate) is True

def test_validate_rate_within_threshold():
    conn = MagicMock()
    mock_latest = {"buy_rate": 5.0, "sell_rate": 5.0}
    with patch("app.services.validation_service.get_latest_rate_for_entity", return_value=mock_latest):
        # 1% change (within 3% threshold)
        rate = ExchangeRate(currency="EUR", buy=5.05, sell=5.05, timestamp="2026-08-01T00:00:00Z")
        assert validate_rate(conn, 1, rate, max_deviation_pct=0.03) is True

def test_validate_rate_exceeds_threshold():
    conn = MagicMock()
    mock_latest = {"buy_rate": 5.0, "sell_rate": 5.0}
    with patch("app.services.validation_service.get_latest_rate_for_entity", return_value=mock_latest):
        # 5% change (exceeds 3% threshold)
        rate = ExchangeRate(currency="EUR", buy=5.25, sell=5.25, timestamp="2026-08-01T00:00:00Z")
        assert validate_rate(conn, 1, rate, max_deviation_pct=0.03) is False
