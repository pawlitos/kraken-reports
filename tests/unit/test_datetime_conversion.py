import unittest
from kraken_reports import convert_utc_to_local_date
from tests.helpers import VerboseTestCase, vprint


class TestDateTimeConversion(VerboseTestCase):

    def test_01_utc_to_local_date_conversion(self):
        """Sprawdza konwersję czasu z UTC na lokalny."""
        cases = [
            # --- Testy dla 12:00 UTC (nigdy nie zmienia daty) ---
            ("2026-07-15 12:00:00", "2026-07-15", "Czas letni: 12:00 -> 14:00 (Ta sama data)"),
            ("2026-12-15 12:00:00", "2026-12-15", "Czas zimowy: 12:00 -> 13:00 (Ta sama data)"),
            # --- Testy dla 23:00 UTC (zawsze zmienia datę) ---
            ("2026-07-14 23:00:00", "2026-07-15", "Czas letni 23:00 -> 01:00 (Zmiana daty)"),
            ("2026-12-16 23:00:00", "2026-12-17", "Czas zimowy 23:00 -> 00:00 (Zmiana daty)"),
            # --- Testy dla 22:00 UTC (data zmienia się TYLKO w czasie letnim) ---
            ("2026-07-14 22:00:00", "2026-07-15", "Czas letni 22:00 -> 00:00 (Zmiana daty)"),
            ("2026-12-16 22:00:00", "2026-12-16", "Czas zimowy 22:00 -> 23:00 (Ta sama data)"),
        ]

        for utc_in, expected_out, desc in cases:
            with self.subTest(utc_in=utc_in):
                output = convert_utc_to_local_date(utc_in)
                vprint(f"  -> {desc}")
                vprint(f"     UTC: {utc_in}")
                vprint(f"     Wynik: {output}")
                vprint(f"     Oczekiwano: {expected_out}")
                self.assertEqual(output, expected_out)


if __name__ == "__main__":
    unittest.main()
