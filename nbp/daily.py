from .base import API_URL, NbpRateFetcher


class DailyNbpRateFetcher(NbpRateFetcher):
    """Pobiera kurs osobnym zapytaniem dla każdego dnia."""

    def _fetch(self, date):
        day = date.strftime("%Y-%m-%d")
        for effective_date, mid in self._request_rates(f"{API_URL}/{day}/?format=json", day):
            self._cache[effective_date] = mid
        self._fetched_days.add(day)
