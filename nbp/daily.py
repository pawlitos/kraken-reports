from datetime import date, timedelta

from .api import API_URL, MAX_LOOKBACK_DAYS, request_rates, today_in_warsaw
from .base import NbpRateFetcher


class DailyNbpRateFetcher(NbpRateFetcher):
    """
    Pobiera kurs USD/PLN osobnym zapytaniem dla każdego dnia, na żądanie.

    get_rate() zwraca kurs z dnia poprzedzającego transakcję, cofając się
    w razie braku tabeli (weekend/święto). Wynik każdego dnia trafia do cache,
    także brak tabeli (None), więc żaden dzień nie jest odpytywany dwa razy.
    """

    def __init__(self):
        self._cache = {}  # 'YYYY-MM-DD' -> kurs albo None (brak tabeli)

    def prefetch(self, first_date_str, last_date_str):
        """Nic nie robi: fetcher dzienny pobiera kursy na żądanie w get_rate()."""

    def get_rate(self, date_str):
        transaction_date = date.fromisoformat(date_str)
        current_date = transaction_date - timedelta(days=1)
        oldest_date = transaction_date - timedelta(days=MAX_LOOKBACK_DAYS)
        today_date = today_in_warsaw()

        while current_date >= oldest_date:
            if current_date <= today_date:  # dni z przyszłości pomijamy: NBP nie ma jeszcze tabeli
                key = current_date.isoformat()

                if key not in self._cache:
                    rates = request_rates(f"{API_URL}/{key}/?format=json", key)
                    self._cache[key] = rates[0][1] if rates else None  # None = NBP nie opublikował tabeli

                if self._cache[key] is not None:
                    return self._cache[key]

            current_date -= timedelta(days=1)

        raise RuntimeError(f"Brak tabeli kursów NBP w ciągu {MAX_LOOKBACK_DAYS} dni przed {date_str}")
