"""Conversions between algebraic square names and 0-63 board indices.

Index layout matches the convention used by most engine protocols: a1 is 0,
b1 is 1, ... h1 is 7, a2 is 8, and so on up to h8 at 63. Keeping that mapping
explicit here means every other module can trade in plain integers or plain
strings without carrying a board object around.
"""

FILES = "abcdefgh"
RANKS = "12345678"


def is_valid_square(square: str) -> bool:
    return (
        isinstance(square, str)
        and len(square) == 2
        and square[0] in FILES
        and square[1] in RANKS
    )


def square_to_index(square: str) -> int:
    if not is_valid_square(square):
        raise ValueError(f"invalid square: {square!r}")
    file_index = FILES.index(square[0])
    rank_index = RANKS.index(square[1])
    return rank_index * 8 + file_index


def index_to_square(index: int) -> str:
    if not isinstance(index, int) or not 0 <= index <= 63:
        raise ValueError(f"index out of range 0-63: {index!r}")
    file_index, rank_index = index % 8, index // 8
    return FILES[file_index] + RANKS[rank_index]


def file_of(square: str) -> str:
    if not is_valid_square(square):
        raise ValueError(f"invalid square: {square!r}")
    return square[0]


def rank_of(square: str) -> str:
    if not is_valid_square(square):
        raise ValueError(f"invalid square: {square!r}")
    return square[1]


def square_color(square: str) -> str:
    """Return "light" or "dark", the color of the square in a standard setup."""
    index = square_to_index(square)
    file_index, rank_index = index % 8, index // 8
    return "light" if (file_index + rank_index) % 2 == 1 else "dark"
