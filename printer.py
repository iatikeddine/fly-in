from typing import List, Dict


class ColoredPrint:
    def __init__(self):
        self.colors: Dict[str, str] = {
            "green": "\033[38;5;46m",
            "red": "\033[38;5;196m",
            "purple": "\033[38;5;129m",
            "black": "\033[38;5;232m",
            "brown": "\033[38;5;94m",
            "orange": "\033[38;5;208m",
            "maroon": "\033[38;5;52m",
            "gold": "\033[38;5;220m",
            "darkred": "\033[38;5;88m",
            "crimson": "\033[38;5;161m",
            "blue": "\033[38;5;33m",
            "yellow": "\033[38;5;226m",
            "cyan": "\033[38;5;51m",
            "lime": "\033[38;5;118m",
            "magenta": "\033[38;5;201m",
            "reset": "\033[0m"
        }

    def print_log(self, log: str, color: str) -> None:
        if color in self.colors:
            ansi: str = self.colors[color]
            reset: str = self.colors["reset"]
            print(f"{ansi}{log}{reset}", end="")
        elif color == "rainbow":
            rainbow_colors: List[str] = [
                "\033[38;5;196m",
                "\033[38;5;208m",
                "\033[38;5;226m",
                "\033[38;5;46m",
                "\033[38;5;33m",
                "\033[38;5;54m",
                "\033[38;5;135m"
            ]
            i: int = 0
            for c in log:
                if i == 7:
                    i = 0
                print(f"{rainbow_colors[i]}{c}", end="")
                i += 1
            print(self.colors["reset"], end="")
        else:
            print(log, end="")
