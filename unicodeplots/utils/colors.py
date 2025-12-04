from enum import IntEnum

INVALID_COLOR = -1


class ColorType(IntEnum):
    """ANSI color codes with named constants and integer compatibility"""

    INVALID = INVALID_COLOR
    BLUE = 39
    GREEN = 114
    RED = 196
    WHITE = 15
    BLACK = 0
    ORANGE = 208
    YELLOW = 226
    PURPLE = 129

    @classmethod
    def from_string(cls, value):
        """Convert string to ColorType, case-insensitive"""
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            try:
                return cls(value)
            except ValueError:
                return cls.INVALID
        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                return cls.INVALID
        return cls.INVALID

    def ansi_prefix(self) -> str:
        """Generate ANSI escape code for the color"""
        if self == ColorType.INVALID:
            return ""
        return f"\033[38;5;{self.value}m"

    def apply(self, text: str) -> str:
        """Apply color to text with reset at end"""
        if self == ColorType.INVALID:
            return text
        return f"{self.ansi_prefix()}{text}\033[0m"


Color = ColorType
