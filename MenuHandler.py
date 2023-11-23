from rich import print
from rich.console import Console
from rich.prompt import IntPrompt


def print_menu(menu_items: list, has_exit=False) -> tuple:
    low, high = 1, len(menu_items)
    for i, item in enumerate(menu_items, start=1):
        print(f"[{i}] {item}")

    if has_exit:
        print("[0] Exit")
        low = 0

    return low, high

def print_titled_menu(title: str, menu_items: list, has_exit=False):
    print(title)
    print_menu(menu_items, has_exit)

def get_choice(selection_range: tuple, prompt: str = "Enter choice", error_message: str = "") -> int:
    console = Console()
    low, high = selection_range
    while True:
        choice = IntPrompt.ask(prompt)
        if in_range(choice, low, high) != -1:
            return choice
        error_to_print = error_message if error_message != "" else f"Please enter a number between {low} and {high}."
        console.print(error_to_print, style="bold red")

def in_range(s: str, min_val: int, max_val: int):
    num = parse_non_negative_int(s)

    if min_val < 0 or max_val < 0:
        raise ValueError("min and max must be non-negative")

    if min_val > max_val:
        min_val, max_val = max_val, min_val

    if num == -1 or num < min_val or num > max_val:
        return -1

    return num

def parse_non_negative_int(s):
    try:
        num = int(s)
        return num if num >= 0 else -1
    except ValueError:
        return -1