from datetime import timedelta

from .base import API_URL, NbpRateFetcher

RANGE_DAYS = 93  # maksymalny zakres dat w jednym zapytaniu do API NBP


class BulkNbpRateFetcher(NbpRateFetcher):
    """Pobiera kursy hurtowo, zakresami po RANGE_DAYS dni kończących się na danej dacie."""

    def _fetch(self, date):
        start_date = date - timedelta(days=RANGE_DAYS - 1)
        start = start_date.strftime("%Y-%m-%d")
        end = date.strftime("%Y-%m-%d")

        url = f"{API_URL}/{start}/{end}/?format=json"
        for effective_date, mid in self._request_rates(url, f"{start}..{end}"):
            self._cache[effective_date] = mid

        day = start_date
        while day <= date:
            self._fetched_days.add(day.strftime("%Y-%m-%d"))
            day += timedelta(days=1)
