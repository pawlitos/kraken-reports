import unittest
from kraken_reports import is_taxable_usd_row
from tests.helpers import VerboseTestCase, vprint


class TestTaxableRowFiltering(VerboseTestCase):

    def test_01_is_taxable_usd_row_returns_false(self):
        """Sprawdza przypadki, w których wiersz nie ma znaczenia podatkowego (False)."""
        cases = [
            ({"type": "conversion"}, "Brak klucza 'symbol' w wierszu"),
            ({"symbol": "eur", "type": "conversion"}, "Symbol inny niż 'usd'"),
            ({"symbol": "usd"}, "Brak klucza 'type'"),
            ({"symbol": "usd", "type": "deposit"}, "Typ 'deposit' spoza TAXABLE_TYPES"),
            ({"symbol": "usd", "type": ""}, "Typ pusty spoza TAXABLE_TYPES"),
            ({}, "Brak obu kluczy 'symbol' i 'type'"),
        ]

        for row, desc in cases:
            with self.subTest(row=row):
                result = is_taxable_usd_row(row)
                vprint(f"  -> {desc}")
                vprint(f"     Wiersz: {row}")
                vprint(f"     Wynik: {result}")
                vprint(f"     Oczekiwano: False")
                self.assertFalse(result, desc)

    def test_02_is_taxable_usd_row_returns_true(self):
        """Sprawdza przypadki, w których wiersz ma znaczenie podatkowe (True)."""
        cases = [
            ({"symbol": "usd", "type": "conversion"}, "Typ 'conversion' z TAXABLE_TYPES"),
            ({"symbol": "usd", "type": "funding rate change"}, "Typ 'funding rate change' z TAXABLE_TYPES"),
            ({"symbol": "usd", "type": "futures trade"}, "Typ 'futures trade' z TAXABLE_TYPES"),
            ({"symbol": "usd", "type": "CONVERSION"}, "Typ wielkimi literami"),
            ({"symbol": "usd", "type": "  conversion  "}, "Typ z białymi znakami wokół"),
            ({"symbol": "USD", "type": "conversion"}, "Symbol wielkimi literami"),
        ]

        for row, desc in cases:
            with self.subTest(row=row):
                result = is_taxable_usd_row(row)
                vprint(f"  -> {desc}")
                vprint(f"     Wiersz: {row}")
                vprint(f"     Wynik: {result}")
                vprint(f"     Oczekiwano: True")
                self.assertTrue(result, desc)


if __name__ == "__main__":
    unittest.main()
