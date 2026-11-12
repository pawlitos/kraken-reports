"""Wspólne funkcje do odpytywania API NBP, używane przez oba fetchery."""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

API_URL = "http://api.nbp.pl/api/exchangerates/rates/a/usd"
MAX_LOOKBACK_DAYS = 31  # tyle dni wstecz szukamy tabeli, zanim zgłosimy błąd


def today_in_warsaw():
    """Dzisiejsza data w Polsce. NBP odrzuca daty późniejsze niż ta (HTTP 400)."""
    return datetime.now(ZoneInfo("Europe/Warsaw")).date()


def request_rates(url, label):
    """
    Zwraca listę (data, kurs) z API NBP lub [] przy 404 (brak tabeli).
    Odpowiedź 200 z pustą listą 'rates' to błąd API, a nie brak tabeli.
    """
    try:
        time.sleep(0.5)
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            rates = [(entry["effectiveDate"], entry["mid"]) for entry in data["rates"]]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Nieoczekiwana odpowiedź API NBP dla {label}: {e}") from e

    if not rates:
        raise RuntimeError(f"Nieoczekiwana odpowiedź API NBP dla {label}: pusta lista 'rates'")
    return rates
