import json
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

API_URL = "http://api.nbp.pl/api/exchangerates/rates/a/usd"
MAX_LOOKBACK_DAYS = 31  # tyle dni wstecz szukamy tabeli, zanim zgłosimy błąd


class NbpRateFetcher(ABC):
    """
    Wspólny interfejs fetcherów kursu USD/PLN z API NBP.

    get_rate() zwraca kurs z dnia poprzedzającego podaną datę, cofając się
    wstecz w razie braku tabeli (weekend/święto). Podklasy decydują tylko
    o tym, jak pobierają dane (_fetch). Każda instancja trzyma własny cache,
    więc łatwo go zresetować lub podmienić w testach.
    """

    def __init__(self):
        self._cache = {}  # data -> kurs (tylko dni z opublikowaną tabelą)
        self._fetched_days = set()  # dni, o które już pytaliśmy API

    def get_rate(self, date_str):
        current_date = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)
        oldest_date = current_date - timedelta(days=MAX_LOOKBACK_DAYS - 1)

        while current_date >= oldest_date:
            formatted_date = current_date.strftime("%Y-%m-%d")
            if formatted_date in self._cache:
                return self._cache[formatted_date]

            if formatted_date in self._fetched_days:
                # dzień już sprawdzony, a tabeli brak -> weekend/święto
                current_date -= timedelta(days=1)
            else:
                self._fetch(current_date)

        raise RuntimeError(f"Brak tabeli kursów NBP w ciągu {MAX_LOOKBACK_DAYS} dni przed {date_str}")

    @abstractmethod
    def _fetch(self, date):
        """
        Pobiera kursy obejmujące co najmniej `date`: wpisuje je do _cache
        i oznacza w _fetched_days wszystkie sprawdzone dni.
        """

    def _request_rates(self, url, label):
        """Zwraca listę wpisów 'rates' z API NBP lub [] przy 404 (brak tabeli)."""
        try:
            time.sleep(0.5)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                return [(entry["effectiveDate"], entry["mid"]) for entry in data["rates"]]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            raise
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Nieoczekiwana odpowiedź API NBP dla {label}: {e}") from e
