import argparse
import csv


def collect_unique_types(path):
    unique_types = set()

    with open(path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if "type" in row and row["type"]:
                unique_types.add(row["type"].strip())

    return unique_types


def main():
    parser = argparse.ArgumentParser(description="Wypisuje unikalne typy transakcji z eksportu Kraken Ledgers.")
    parser.add_argument("path", help="Ścieżka do pliku CSV z eksportem Kraken Ledgers")
    args = parser.parse_args()

    unique_types = collect_unique_types(args.path)

    print("Wszystkie unikalne typy transakcji w pliku:")
    print("-" * 40)
    for t in sorted(unique_types):
        print(t)


if __name__ == "__main__":
    main()
