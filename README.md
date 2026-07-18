# Kraken Reports

Narzędzie do rozliczania podatkowego transakcji USD z eksportu Kraken Ledgers. Przelicza przychody i koszty w USD na PLN według kursów średnich NBP, tak jak wymaga tego polski urząd skarbowy, i wypisuje roczne podsumowanie.

## Jak to działa

1. Wczytuje plik CSV wyeksportowany z Kraken (Ledgers).
2. Filtruje wiersze dotyczące symbolu `usd` o typach mających znaczenie podatkowe:
   - `conversion`
   - `funding rate change`
   - `futures trade`
3. Dla każdego wiersza:
   - konwertuje datę i czas transakcji z UTC na datę lokalną w strefie `Europe/Warsaw` (z uwzględnieniem czasu letniego/zimowego),
   - pobiera kurs średni USD/PLN z API NBP dla dnia poprzedzającego transakcję (zgodnie z zasadami rozliczania podatkowego), z automatycznym cofaniem się wstecz, gdy dany dzień nie ma opublikowanej tabeli kursów (weekendy, święta),
   - przelicza kwotę USD na PLN.
4. Sumuje osobno przychody i koszty (w USD i PLN) i wypisuje podsumowanie roczne.

## Struktura projektu

| Plik | Opis |
|---|---|
| [kraken_reports.py](kraken_reports.py) | Główny skrypt — wczytuje CSV, filtruje i przelicza transakcje, wypisuje podsumowanie. |
| [nbp.py](nbp.py) | `NbpRateFetcher` — pobiera i cache'uje kursy USD/PLN z publicznego API NBP. |
| [unique.py](unique.py) | Pomocniczy skrypt do podglądu unikalnych wartości kolumny `type` w pliku `kraken_ledgers.csv`. |
| [tests/unit/](tests/unit/) | Testy jednostkowe (bez sieci) — logika konwersji dat, filtrowanie wierszy itp. |
| [tests/integration/](tests/integration/) | Testy integracyjne odpytujące realne API NBP. |

## Wymagania

- Python 3.9+ (wykorzystywane jest `zoneinfo`)
- Brak zewnętrznych zależności — projekt korzysta wyłącznie z biblioteki standardowej

## Użycie

```bash
python kraken_reports.py sciezka/do/kraken_ledgers.csv
```

Przykładowy wynik:

```
=============================================
PODSUMOWANIE ROCZNE USD (Bez zaokrągleń):
=============================================
Suma przychodów USD:       1,234.56789000 USD
Suma kosztów USD:          12.34000000 USD
WYNIK NETTO USD:           1,222.22789000 USD

=============================================
PODSUMOWANIE ROCZNE PLN (Do urzędu skarbowego):
=============================================
Suma przychodów (zyski):   4,987.65 PLN
Suma kosztów (opłaty):     49.87 PLN
WYNIK NETTO PLN:           4,937.78 PLN
```

## Testy

Testy jednostkowe (bez połączenia z siecią):

```bash
python -m unittest discover -s tests/unit -v
```

Testy integracyjne (wymagają połączenia z API NBP):

```bash
python -m unittest discover -s tests/integration -v
```

Wszystkie testy naraz:

```bash
python -m unittest discover -s tests -v
```

## Uwaga

Narzędzie ma charakter pomocniczy i nie zastępuje profesjonalnej porady podatkowej. Przed złożeniem rozliczenia warto zweryfikować wyniki samodzielnie lub z doradcą podatkowym.
