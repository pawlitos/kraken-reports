from .bulk import BulkNbpRateFetcher
from .daily import DailyNbpRateFetcher

FETCHERS = {
    "daily": DailyNbpRateFetcher,
    "bulk": BulkNbpRateFetcher,
}


def create_rate_fetcher(mode):
    """Zwraca fetcher kursów NBP dla podanego trybu ('daily' lub 'bulk')."""
    return FETCHERS[mode]()
