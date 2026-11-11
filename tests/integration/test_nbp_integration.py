import json
import unittest
import urllib.request

from nbp import BulkNbpRateFetcher, DailyNbpRateFetcher, create_rate_fetcher
from tests.helpers import CYAN, GREEN, RED, YELLOW, VerboseTestCase, vprint


class TestApiRawJson(VerboseTestCase):

    def test_01_real_nbp_api_raw_json(self):
        """Sprawdza strukturę JSON zwracaną przez API NBP (klucze 'rates', 'mid', 'effectiveDate')."""
        url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/2026-07-14/?format=json"

        vprint(f"-> Adres URL: {url}", CYAN)

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req) as response:
            vprint(f"-> Kod odpowiedzi serwera: {response.status}", CYAN)
            self.assertEqual(response.status, 200)

            # Dekodujemy i ładujemy surowy JSON
            raw_data = response.read().decode("utf-8")
            data = json.loads(raw_data)

            vprint("-> Otrzymany JSON z NBP:", CYAN)
            vprint(json.dumps(data, indent=2), YELLOW)

            # Sprawdzamy obecność kluczowych pól, od których zależy Twój parser
            self.assertIn("rates", data, "Brak klucza 'rates' w odpowiedzi API NBP")
            self.assertIsInstance(data["rates"], list)
            self.assertGreater(len(data["rates"]), 0)

            first_rate_entry = data["rates"][0]
            self.assertIn("mid", first_rate_entry, "Brak klucza 'mid' wewnątrz tabeli rates")
            self.assertIn("effectiveDate", first_rate_entry)

            # Sprawdzamy, czy data w tabeli to faktycznie ta, o którą pytaliśmy
            vprint(f"-> Data publikacji tabeli w JSON: '{first_rate_entry['effectiveDate']}'", CYAN)
            vprint(f"-> Kurs średni (mid) w JSON: {first_rate_entry['mid']} PLN", CYAN)

            self.assertEqual(first_rate_entry["effectiveDate"], "2026-07-14")
            vprint("-> [OK] Walidacja struktury JSON zakończona sukcesem", GREEN)

    def test_02_real_nbp_api_range_raw_json(self):
        """Sprawdza strukturę JSON dla zakresu dat (zapytanie używane przez fetcher hurtowy)."""
        url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/2026-07-10/2026-07-14/?format=json"

        vprint(f"-> Adres URL: {url}", CYAN)

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req) as response:
            vprint(f"-> Kod odpowiedzi serwera: {response.status}", CYAN)
            self.assertEqual(response.status, 200)

            # Dekodujemy i ładujemy surowy JSON
            raw_data = response.read().decode("utf-8")
            data = json.loads(raw_data)

            vprint("-> Otrzymany JSON z NBP:", CYAN)
            vprint(json.dumps(data, indent=2), YELLOW)

            # Sprawdzamy obecność listy 'rates'
            self.assertIn("rates", data, "Brak klucza 'rates' w odpowiedzi API NBP")
            self.assertIsInstance(data["rates"], list)

            # Każdy wpis musi mieć pola, z których korzysta fetcher hurtowy
            for entry in data["rates"]:
                self.assertIn("mid", entry, "Brak klucza 'mid' wewnątrz tabeli rates")
                self.assertIn("effectiveDate", entry)
                vprint(f"-> {entry['effectiveDate']}: {entry['mid']} PLN", CYAN)

            # Zakres pt 10.07 - wt 14.07: tylko dni robocze, bez soboty i niedzieli
            effective_dates = [entry["effectiveDate"] for entry in data["rates"]]
            self.assertEqual(effective_dates, ["2026-07-10", "2026-07-13", "2026-07-14"])
            vprint("-> [OK] Walidacja struktury JSON zakończona sukcesem, zakres zawiera tylko dni robocze, bez weekendu", GREEN)


class FetcherIntegrationTests:
    """Wspólne testy fetcherów; podklasy ustawiają FETCHER_MODE."""

    FETCHER_MODE = None

    def setUp(self):
        super().setUp()
        self.rate_fetcher = create_rate_fetcher(self.FETCHER_MODE)

    def test_03_real_nbp_api_weekend_and_weekdays_fallback(self):
        """Sprawdza cofanie się do poprzedniego dnia roboczego dla weekendów i dni granicznych."""
        # Scenariusze dla lipca 2026 roku:
        # Piątek (10.07)      -> API szuka czwartku (09.07) -> Działa (Roboczy)
        # Sobota (11.07)      -> API szuka piątku (10.07) -> Działa (Roboczy)
        # Niedziela (12.07)    -> API szuka soboty (404) -> cofa do piątku (10.07) -> Działa
        # Poniedziałek (13.07) -> API szuka niedzieli (404) -> soboty (404) -> piątku (10.07) -> Działa
        # Wtorek (14.07)       -> API szuka poniedziałku (13.07) -> Działa (Roboczy)
        # Środa (15.07)        -> API szuka wtorku (14.07) -> Działa (Roboczy)

        scenarios = [
            ("2026-07-10", "Piątek (Szukamy kursu z czwartku 09.07)"),
            ("2026-07-11", "Sobota (Szukamy kursu z piątku 10.07)"),
            ("2026-07-12", "Niedziela (Szukamy soboty, potem piątku 10.07)"),
            ("2026-07-13", "Poniedziałek (Szukamy niedzieli, soboty, potem piątku 10.07)"),
            ("2026-07-14", "Wtorek (Szukamy kursu z poniedziałku 13.07)"),
            ("2026-07-15", "Środa (Szukamy kursu z wtorku 14.07)"),
        ]

        for test_date, description in scenarios:
            vprint(f"-> Testuję dzień: {description}", CYAN)
            vprint(f"   Data przekazana do funkcji: '{test_date}'", CYAN)

            try:
                rate = self.rate_fetcher.get_rate(test_date)
                vprint(f"   Odebrano realny kurs z API NBP: {rate} PLN/USD", CYAN)

                # Asercje sprawdzające poprawność danych z sieci
                self.assertIsInstance(rate, float)
                self.assertTrue(3.0 < rate < 6.0, f"Kurs {rate} PLN/USD jest poza zakresem.")
                vprint("   [OK] Sukces połączenia i poprawnego wyznaczenia daty kursu.", GREEN)

            except (OSError, RuntimeError) as e:
                vprint(f"   [BŁĄD] Funkcja zawiodła dla dnia: {test_date}", RED)
                self.fail(f"Test integracyjny nie powiódł się dla {test_date}: {e}")

    def test_04_real_nbp_api_exact_rate_from_previous_business_day(self):
        """Sprawdza, czy kurs pochodzi dokładnie z ostatniego dnia roboczego przed transakcją.

        Każdy scenariusz to osobny subTest z nowym fetcherem (pusty cache), więc wynik
        nie zależy od kolejności scenariuszy, a błąd jednego dnia nie przerywa pozostałych.
        """
        # Kursy NBP z lipca 2026 roku (opublikowane kursy historyczne się nie zmieniają):
        # czw 09.07 = 3.7692, pt 10.07 = 3.8025, pn 13.07 = 3.7846, wt 14.07 = 3.8076

        scenarios = [
            ("2026-07-10", "09.07", 3.7692),  # piątek -> czwartek
            ("2026-07-11", "10.07", 3.8025),  # sobota -> piątek
            ("2026-07-12", "10.07", 3.8025),  # niedziela -> piątek
            ("2026-07-13", "10.07", 3.8025),  # poniedziałek -> piątek
            ("2026-07-14", "13.07", 3.7846),  # wtorek -> poniedziałek
            ("2026-07-15", "14.07", 3.8076),  # środa -> wtorek
        ]

        for test_date, rate_day, expected_rate in scenarios:
            with self.subTest(date=test_date):
                fetcher = create_rate_fetcher(self.FETCHER_MODE)
                vprint(f"-> Transakcja: '{test_date}', oczekiwany kurs z {rate_day}: {expected_rate} PLN/USD", CYAN)

                try:
                    rate = fetcher.get_rate(test_date)
                    vprint(f"   Odebrano kurs z API NBP: {rate} PLN/USD", CYAN)

                    self.assertEqual(rate, expected_rate, f"Zły kurs dla transakcji z {test_date}")
                    vprint(f"   [OK] Kurs pochodzi z właściwego dnia ({rate_day})", GREEN)

                except (OSError, RuntimeError) as e:
                    vprint(f"   [BŁĄD] Funkcja zawiodła dla dnia: {test_date}", RED)
                    self.fail(f"Test integracyjny nie powiódł się dla {test_date}: {e}")


class TestDailyFetcherIntegration(FetcherIntegrationTests, VerboseTestCase):
    FETCHER_MODE = "daily"

    def test_05_factory_returns_daily_fetcher(self):
        self.assertIsInstance(self.rate_fetcher, DailyNbpRateFetcher)


class TestBulkFetcherIntegration(FetcherIntegrationTests, VerboseTestCase):
    FETCHER_MODE = "bulk"

    def test_05_factory_returns_bulk_fetcher(self):
        self.assertIsInstance(self.rate_fetcher, BulkNbpRateFetcher)

    def test_06_matches_daily_fetcher(self):
        """Fetcher hurtowy musi zwracać te same kursy co dzienny."""
        daily = create_rate_fetcher("daily")
        for test_date in ["2026-07-10", "2026-07-13", "2026-07-15"]:
            self.assertEqual(self.rate_fetcher.get_rate(test_date), daily.get_rate(test_date), test_date)


if __name__ == "__main__":
    unittest.main()
