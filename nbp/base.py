from abc import ABC, abstractmethod


class NbpRateFetcher(ABC):
    """
    Wspólny kontrakt fetcherów kursu USD/PLN z API NBP.

    Klasa jest w pełni abstrakcyjna: nie zawiera żadnej logiki, określa tylko,
    jakie metody musi mieć każdy fetcher. Dzięki temu kraken_reports.py może
    korzystać z dowolnego z nich w ten sam sposób.
    """

    @abstractmethod
    def prefetch(self, first_date_str, last_date_str):
        """
        Przygotowuje kursy dla transakcji z zakresu dat first..last (włącznie,
        format 'YYYY-MM-DD'). Wywoływana raz, przed pierwszym get_rate().
        """

    @abstractmethod
    def get_rate(self, date_str):
        """
        Zwraca kurs średni USD/PLN z ostatniego dnia roboczego przed datą
        transakcji ('YYYY-MM-DD').
        """
