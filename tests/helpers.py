import os
import sys
import unittest

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

# Kolory ANSI do przekazania jako drugi argument vprint().
# Wyłączone przy przekierowaniu do pliku lub gdy ustawiono zmienną NO_COLOR.
CYAN, GREEN, RED, YELLOW, RESET = "\033[36m", "\033[32m", "\033[31m", "\033[33m", "\033[0m"
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _enable_windows_ansi():
    """Włącza obsługę kolorów ANSI w klasycznej konsoli Windows (cmd, PowerShell)."""
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING


if USE_COLOR and os.name == "nt":
    _enable_windows_ansi()


def vprint(text="", color=None):
    """Wypisuje tekst w trybie -v; `color` to np. CYAN, GREEN, RED (domyślnie bez koloru)."""
    if VERBOSE:
        if USE_COLOR and color:
            text = f"{color}{text}{RESET}"
        print(text, flush=True)


class VerboseTestCase(unittest.TestCase):
    def setUp(self):
        vprint()
