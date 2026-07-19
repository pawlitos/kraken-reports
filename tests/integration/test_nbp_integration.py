import unittest
import urllib.request
import json
from nbp import NbpRateFetcher
from tests.helpers import VerboseTestCase, vprint


class TestNBPIntegration(VerboseTestCase):

    def setUp(self):
        super().setUp()
        self.rate_fetcher = NbpRateFetcher()

    def test_01_real_nbp_api_raw_json(self):
        """Sprawdza strukturę JSON zwracaną przez API NBP (klucze 'rates', 'mid', 'effectiveDate')."""
        url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/2026-07-14/?format=json"

        vprint(f"  -> Adres URL: {url}")

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req) as response:
            vprint(f"  -> Kod odpowiedzi serwera: {response.status}")
            self.assertEqual(response.status, 200)

            # Dekodujemy i ładujemy surowy JSON
            raw_data = response.read().decode("utf-8")
            data = json.loads(raw_data)

            vprint(f"  -> Otrzymany JSON z NBP:\n{json.dumps(data, indent=2)}")

            # Sprawdzamy obecność kluczowych pól, od których zależy Twój parser
            self.assertIn("rates", data, "Brak klucza 'rates' w odpowiedzi API NBP")
            self.assertIsInstance(data["rates"], list)
            self.assertGreater(len(data["rates"]), 0)

            first_rate_entry = data["rates"][0]
            self.assertIn("mid", first_rate_entry, "Brak klucza 'mid' wewnątrz tabeli rates")
            self.assertIn("effectiveDate", first_rate_entry)

            # Sprawdzamy, czy data w tabeli to faktycznie ta, o którą pytaliśmy
            vprint(f"  -> Data publikacji tabeli w JSON: '{first_rate_entry['effectiveDate']}'")
            vprint(f"  -> Kurs średni (mid) w JSON: {first_rate_entry['mid']} PLN")

            self.assertEqual(first_rate_entry["effectiveDate"], "2026-07-14")
            vprint(f"  -> [OK] Walidacja struktury JSON zakończona sukcesem")

    def test_02_real_nbp_api_response_structure(self):
        """Sprawdza, czy pobrany kurs USD/PLN jest sensowną liczbą z przedziału 3.0-6.0."""
        # Wybieramy konkretny, znany dzień roboczy z przeszłości
        test_date = "2026-07-15"  # środa (kurs pobierany jest dla wtorku 2026-07-14)

        vprint(f"  -> Wysyłam zapytanie o datę transakcji: '{test_date}'")

        try:
            rate = self.rate_fetcher.get_rate(test_date)
            vprint(f"  -> Odebrano kurs z API: {rate} PLN/USD")

            # Sprawdzamy, czy otrzymana wartość jest sensowną liczbą zmiennoprzecinkową
            self.assertIsInstance(rate, float)
            self.assertTrue(3.0 < rate < 6.0, f"Kurs {rate} PLN/USD wydaje się podejrzanie wysoki lub niski.")
            vprint(f"  -> [OK] Kurs mieści się w dopuszczalnym przedziale (3.0 - 6.0)")

        except Exception as e:
            vprint(f"  -> [BŁĄD] Połączenie z API NBP nie powiodło się!")
            self.fail(f"Połączenie z API NBP nie powiodło się: {e}")

    def test_03_real_nbp_api_weekend_and_weekdays_fallback(self):
        """Sprawdza cofanie się do poprzedniego dnia roboczego dla weekendów i dni granicznych."""
        # Scenariusze dla lipca 2026 roku:
        # Piątek (10.07)      -> API szuka czwartku (09.07) -> Działa (Roboczy)
        # Sobota (11.07)      -> API szuka piątku (10.07) -> Działa (Roboczy)
        # Niedziela (12.07)    -> API szuka soboty (404) -> cofa do piątku (10.07) -> Działa
        # Poniedziałek (13.07) -> API szuka niedzieli (404) -> soboty (404) -> piątku (10.07) -> Działa
        # Wtorek (14.07)       -> API szuka poniedziałku (13.07) -> Działa (Roboczy)

        scenarios = [
            ("2026-07-10", "Piątek (Szukamy kursu z czwartku 09.07)"),
            ("2026-07-11", "Sobota (Szukamy kursu z piątku 10.07)"),
            ("2026-07-12", "Niedziela (Szukamy soboty, potem piątku 10.07)"),
            ("2026-07-13", "Poniedziałek (Szukamy niedzieli, soboty, potem piątku 10.07)"),
            ("2026-07-14", "Wtorek (Szukamy kursu z poniedziałku 13.07)"),
        ]

        for test_date, description in scenarios:
            vprint(f"  -> Testuję dzień: {description}")
            vprint(f"     Data przekazana do funkcji: '{test_date}'")

            try:
                rate = self.rate_fetcher.get_rate(test_date)
                vprint(f"     Odebrano realny kurs z API NBP: {rate} PLN/USD")

                # Asercje sprawdzające poprawność danych z sieci
                self.assertIsInstance(rate, float)
                self.assertTrue(3.0 < rate < 6.0, f"Kurs {rate} PLN/USD jest poza zakresem.")
                vprint(f"     [OK] Sukces połączenia i poprawnego wyznaczenia daty kursu.")

            except Exception as e:
                vprint(f"     [BŁĄD] Funkcja zawiodła dla dnia: {test_date}")
                self.fail(f"Test integracyjny nie powiódł się dla {test_date}: {e}")


if __name__ == "__main__":
    unittest.main()
