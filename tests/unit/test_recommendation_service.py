import unittest
from unittest.mock import MagicMock, patch

from app.models.recommendation import MarketStats
from app.services.recommendation_service import (
    get_market_stats,
    rank_own_rate,
    recommend_rate,
)


class TestRecommendationService(unittest.TestCase):
    def test_get_market_stats(self):
        mock_conn = MagicMock()
        mock_rates = [
            {"entity_id": 1, "name": "Comp A", "buy_rate": 4.95, "sell_rate": 5.00},
            {"entity_id": 2, "name": "Comp B", "buy_rate": 4.97, "sell_rate": 4.99},
            {"entity_id": 3, "name": "Comp C", "buy_rate": 4.96, "sell_rate": 5.01},
        ]

        with (
            patch("app.services.recommendation_service.get_own_office_entity_id", return_value=99),
            patch("app.services.recommendation_service.get_latest_rates_by_currency", return_value=mock_rates),
        ):
            stats = get_market_stats(mock_conn, "EUR")

            self.assertEqual(stats.currency, "EUR")
            self.assertEqual(stats.best_buy, 4.97)
            self.assertEqual(stats.best_sell, 4.99)
            self.assertEqual(stats.avg_buy, 4.96)
            self.assertEqual(stats.avg_sell, 5.00)
            self.assertEqual(stats.competitor_count, 3)

    def test_recommend_rate_beat_best_normal(self):
        mock_conn = MagicMock()
        mock_stats = MarketStats(
            currency="EUR",
            best_buy=4.95,
            best_sell=5.05,
            avg_buy=4.90,
            avg_sell=5.10,
            competitor_count=3,
        )

        with patch("app.services.recommendation_service.get_market_stats", return_value=mock_stats):
            rec = recommend_rate(mock_conn, "EUR", strategy="beat_best", margin=0.002, min_spread=0.01)

            self.assertEqual(rec.recommended_buy, 4.952)
            self.assertEqual(rec.recommended_sell, 5.048)
            self.assertEqual(rec.spread, round(5.048 - 4.952, 4))
            self.assertFalse(rec.is_fallback)
            self.assertEqual(rec.strategy_used, "beat_best")

    def test_recommend_rate_beat_best_fallback_triggered(self):
        mock_conn = MagicMock()
        mock_stats = MarketStats(
            currency="EUR",
            best_buy=4.999,
            best_sell=5.001,
            avg_buy=4.950,
            avg_sell=5.050,
            competitor_count=3,
        )

        with patch("app.services.recommendation_service.get_market_stats", return_value=mock_stats):
            rec = recommend_rate(mock_conn, "EUR", strategy="beat_best", margin=0.002, min_spread=0.01)

            self.assertTrue(rec.is_fallback)
            self.assertEqual(rec.strategy_used, "fallback_match_average")
            self.assertEqual(rec.recommended_buy, 4.950)
            self.assertEqual(rec.recommended_sell, 5.050)
            self.assertEqual(rec.spread, 0.100)

    def test_rank_own_rate(self):
        mock_conn = MagicMock()
        mock_all_rates = [
            {"entity_id": 99, "name": "Own Office", "buy_rate": 4.96, "sell_rate": 5.00},
            {"entity_id": 1, "name": "Comp A", "buy_rate": 4.98, "sell_rate": 5.02},
            {"entity_id": 2, "name": "Comp B", "buy_rate": 4.95, "sell_rate": 4.99},
            {"entity_id": 3, "name": "Comp C", "buy_rate": 4.94, "sell_rate": 5.03},
        ]

        with (
            patch("app.services.recommendation_service.get_own_office_entity_id", return_value=99),
            patch("app.services.recommendation_service.get_latest_rates_by_currency", return_value=mock_all_rates),
        ):
            ranking = rank_own_rate(mock_conn, "EUR")

            self.assertEqual(ranking.currency, "EUR")
            self.assertEqual(ranking.own_buy, 4.96)
            self.assertEqual(ranking.own_sell, 5.00)
            self.assertEqual(ranking.buy_rank, 2)
            self.assertEqual(ranking.sell_rank, 2)
            self.assertEqual(ranking.total_competitors, 3)
            self.assertEqual(ranking.buy_rank_text, "#2 of 3 on buy")
            self.assertEqual(ranking.sell_rank_text, "#2 of 3 on sell")


if __name__ == "__main__":
    unittest.main()
