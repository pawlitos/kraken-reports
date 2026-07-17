import argparse
import csv
from datetime import datetime
from zoneinfo import ZoneInfo

from nbp import NbpRateFetcher

TAXABLE_TYPES = {"conversion", "funding rate change", "futures trade"}


def convert_utc_to_local_date(date_str):
    """
    Konwertuje datę i czas UTC ('YYYY-MM-DD HH:MM:SS') na datę lokalną
    w strefie Europe/Warsaw (uwzględnia czas letni/zimowy).
    Zwraca datę w formacie 'YYYY-MM-DD'.
    """
    utc_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("UTC"))
    local_dt = utc_dt.astimezone(ZoneInfo("Europe/Warsaw"))
    return local_dt.strftime("%Y-%m-%d")


def is_taxable_usd_row(row):
    """Sprawdza, czy wiersz dotyczy USD i ma znaczenie podatkowe."""
    if row.get("symbol") != "usd":
        return False
    transaction_type = row.get("type", "").lower().strip()
    return transaction_type in TAXABLE_TYPES


def process_row(date_time_str, change_str, rate_fetcher):
    """
    Przetwarza pojedynczy wiersz: liczy datę lokalną, kurs NBP i kwotę w PLN.
    Zwraca kwotę USD i PLN (do sumowań).
    """
    local_date_str = convert_utc_to_local_date(date_time_str)
    rate = rate_fetcher.get_rate(local_date_str)

    amount_usd = float(change_str)
    amount_pln = round(amount_usd * rate, 2)

    return amount_usd, amount_pln


def print_summary(total_income_usd, total_expenses_usd, total_income_pln, total_expenses_pln):
    net_usd = total_income_usd - total_expenses_usd
    net_pln = total_income_pln - total_expenses_pln

    print("\n" + "=" * 45)
    print("PODSUMOWANIE ROCZNE USD (Bez zaokrągleń):")
    print("=" * 45)
    print(f"Suma przychodów USD:       {total_income_usd:,.8f} USD")
    print(f"Suma kosztów USD:          {total_expenses_usd:,.8f} USD")
    print(f"WYNIK NETTO USD:           {net_usd:,.8f} USD")

    print("\n" + "=" * 45)
    print("PODSUMOWANIE ROCZNE PLN (Do urzędu skarbowego):")
    print("=" * 45)
    print(f"Suma przychodów (zyski):   {total_income_pln:,.2f} PLN")
    print(f"Suma kosztów (opłaty):     {total_expenses_pln:,.2f} PLN")
    print(f"WYNIK NETTO PLN:           {net_pln:,.2f} PLN")


def main():
    parser = argparse.ArgumentParser(description="Generuje rozliczenie PLN na podstawie eksportu Kraken Ledgers.")
    parser.add_argument("path", help="Ścieżka do pliku CSV z eksportem Kraken Ledgers")
    args = parser.parse_args()

    rate_fetcher = NbpRateFetcher()

    total_income_pln = 0.0
    total_expenses_pln = 0.0
    total_income_usd = 0.0
    total_expenses_usd = 0.0

    with open(args.path, mode="r", encoding="utf-8") as file_in:
        reader = csv.DictReader(file_in)

        for row in reader:
            if not is_taxable_usd_row(row):
                continue

            try:
                amount_usd, amount_pln = process_row(row["dateTime"], row["change"], rate_fetcher)
            except KeyError as e:
                print(f"Pominięto wiersz — brak kolumny {e} w danych: {row}")
                continue

            if amount_usd > 0:
                total_income_usd += amount_usd
                total_income_pln += amount_pln
            else:
                total_expenses_usd += abs(amount_usd)
                total_expenses_pln += abs(amount_pln)

    print_summary(total_income_usd, total_expenses_usd, total_income_pln, total_expenses_pln)


if __name__ == "__main__":
    main()
