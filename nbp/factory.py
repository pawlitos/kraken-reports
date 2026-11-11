from .bulk import BulkNbpRateFetcher
from .daily import DailyNbpRateFetcher

FETCHERS = {
    "daily": DailyNbpRateFetcher,
    "bulk": BulkNbpRateFetcher,
}


def create_rate_fetcher(mode):
    """Zwraca fetcher kursów NBP dla podanego trybu ('daily' lub 'bulk')."""
    try:
        return FETCHERS[mode]()
    except KeyError:
        raise ValueError(f"Nieznany tryb pobierania kursów: {mode!r} (dostępne: {', '.join(FETCHERS)})") from None
