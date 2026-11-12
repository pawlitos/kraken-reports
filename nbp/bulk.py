from datetime import date, timedelta

from .api import API_URL, MAX_LOOKBACK_DAYS, request_rates, today_in_warsaw
from .base import NbpRateFetcher

RANGE_DAYS = 93  # maksymalny zakres dat w jednym zapytaniu do API NBP


class BulkNbpRateFetcher(NbpRateFetcher):
    """
    Pobiera kursy USD/PLN hurtowo, zanim zaczną się wywołania get_rate().

    prefetch() pobiera wszystkie kursy potrzebne dla transakcji z podanego
    zakresu dat, zapytaniami po RANGE_DAYS dni. get_rate() nie odpytuje już
    API, tylko szuka kursu w pobranych danych, więc kolejność wierszy
    w pliku nie ma znaczenia.
    """

    def __init__(self):
        self._rates = {}  # 'YYYY-MM-DD' -> kurs (tylko dni z opublikowaną tabelą)
        self._first = None  # zakres dat transakcji objęty prefetch()
        self._last = None

    def prefetch(self, first_date_str, last_date_str):
        self._first = date.fromisoformat(first_date_str)
        self._last = date.fromisoformat(last_date_str)

        # Od najdalszego dnia, do którego get_rate może się cofnąć, do dnia przed ostatnią transakcją
        start = self._first - timedelta(days=MAX_LOOKBACK_DAYS)
        end = min(self._last - timedelta(days=1), today_in_warsaw())  # NBP odrzuca przyszłe daty

        chunk_start = start

        while chunk_start <= end:
            chunk_end = min(chunk_start + timedelta(days=RANGE_DAYS - 1), end)
            url = f"{API_URL}/{chunk_start}/{chunk_end}/?format=json"

            for effective_date, mid in request_rates(url, f"{chunk_start}..{chunk_end}"):
                self._rates[effective_date] = mid

            chunk_start = chunk_end + timedelta(days=1)

    def get_rate(self, date_str):
        transaction_date = date.fromisoformat(date_str)

        if self._first is None or not self._first <= transaction_date <= self._last:
            raise RuntimeError(f"Data {date_str} jest poza zakresem pobranym przez prefetch()")

        current_date = transaction_date - timedelta(days=1)
        oldest_date = transaction_date - timedelta(days=MAX_LOOKBACK_DAYS)

        while current_date >= oldest_date:
            key = current_date.isoformat()

            if key in self._rates:
                return self._rates[key]

            current_date -= timedelta(days=1)

        raise RuntimeError(f"Brak tabeli kursów NBP w ciągu {MAX_LOOKBACK_DAYS} dni przed {date_str}")
