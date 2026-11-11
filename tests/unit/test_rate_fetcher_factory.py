import unittest

from nbp import BulkNbpRateFetcher, DailyNbpRateFetcher, NbpRateFetcher, create_rate_fetcher
from tests.helpers import VerboseTestCase


class TestRateFetcherFactory(VerboseTestCase):

    def test_daily_mode_returns_daily_fetcher(self):
        self.assertIsInstance(create_rate_fetcher("daily"), DailyNbpRateFetcher)

    def test_bulk_mode_returns_bulk_fetcher(self):
        self.assertIsInstance(create_rate_fetcher("bulk"), BulkNbpRateFetcher)

    def test_each_call_returns_fresh_instance(self):
        self.assertIsNot(create_rate_fetcher("bulk"), create_rate_fetcher("bulk"))

    def test_unknown_mode_raises_value_error(self):
        with self.assertRaises(ValueError):
            create_rate_fetcher("weekly")

    def test_base_class_is_abstract(self):
        with self.assertRaises(TypeError):
            NbpRateFetcher()


if __name__ == "__main__":
    unittest.main()
