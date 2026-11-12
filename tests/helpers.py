import os
import sys
import unittest

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

# Kolory ANSI do przekazania jako drugi argument vprint().
# Wyłączone przy przekierowaniu do pliku, gdy ustawiono zmienną NO_COLOR
# lub gdy konsola Windows nie pozwala włączyć kolorów ANSI.
CYAN, GREEN, RED, YELLOW, RESET = "\033[36m", "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def _enable_windows_ansi():
    """
    Włącza obsługę kolorów ANSI w klasycznej konsoli Windows (cmd, PowerShell).
    Zwraca True, jeśli się udało; w przeciwnym razie kolory trzeba wyłączyć.
    """
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False
    return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))  # ENABLE_VIRTUAL_TERMINAL_PROCESSING


USE_COLOR = (
    sys.stdout.isatty()
    and "NO_COLOR" not in os.environ
    and (os.name != "nt" or _enable_windows_ansi())
)


def vprint(text="", color=None):
    """Wypisuje tekst w trybie -v; `color` to np. CYAN, GREEN, RED (domyślnie bez koloru)."""
    if VERBOSE:
        if USE_COLOR and color:
            text = f"{color}{text}{RESET}"
        print(text, flush=True)


class VerboseTestCase(unittest.TestCase):
    def setUp(self):
        vprint()
