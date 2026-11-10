import urllib.request
import urllib.error
import json
import time
from datetime import datetime, timedelta


class NbpRateFetcher:
    """
    Pobiera kurs USD/PLN z API NBP dla danego dnia, cofając się wstecz
    w razie braku tabeli (weekend/święto). Trzyma własny cache, więc
    łatwo go zresetować lub podmienić w testach.
    """

    def __init__(self):
        self._cache = {}

    def get_rate(self, date_str):
        current_date = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)

        while True:
            formatted_date = current_date.strftime("%Y-%m-%d")
            if formatted_date in self._cache:
                return self._cache[formatted_date]

            url = f"http://api.nbp.pl/api/exchangerates/rates/a/usd/{formatted_date}/?format=json"
            try:
                time.sleep(0.5)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode())
                    rate = data["rates"][0]["mid"]
                    self._cache[formatted_date] = rate
                    return rate
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    current_date -= timedelta(days=1)
                else:
                    raise
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                raise RuntimeError(f"Nieoczekiwana odpowiedź API NBP dla {formatted_date}: {e}") from e
