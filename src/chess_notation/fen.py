"""Parsing and rendering of Forsyth-Edwards Notation (FEN) position strings.

Like the SAN module, this checks grammar, not legality: a FEN with two white
kings parses fine here, the same way "Nbd7" parses fine even on a board where
no knight could reach d7. Board indices follow the same a1=0 ... h8=63
convention as squares.py, so callers can move a piece string from
`FenPosition.board` straight into whatever else in this library expects a
square index.
"""

from dataclasses import dataclass

from .squares import is_valid_square

_PIECE_LETTERS = set("pnbrqkPNBRQK")


@dataclass(frozen=True)
class CastlingRights:
    white_kingside: bool
    white_queenside: bool
    black_kingside: bool
    black_queenside: bool


@dataclass(frozen=True)
class FenPosition:
    board: tuple
    active_color: str
    castling_rights: CastlingRights
    en_passant_square: str | None
    halfmove_clock: int
    fullmove_number: int


def parse_fen(fen: str) -> FenPosition:
    if not isinstance(fen, str) or not fen.strip():
        raise ValueError("fen must be a non-empty string")

    fields = fen.split()
    if len(fields) != 6:
        raise ValueError(
            f"FEN must have 6 space-separated fields, got {len(fields)}: {fen!r}"
        )
    placement, active_color, castling, en_passant, halfmove, fullmove = fields

    board = _parse_placement(placement)

    if active_color not in ("w", "b"):
        raise ValueError(f"active color must be 'w' or 'b': {active_color!r}")

    castling_rights = _parse_castling(castling)

    if en_passant == "-":
        en_passant_square = None
    elif is_valid_square(en_passant):
        en_passant_square = en_passant
    else:
        raise ValueError(f"invalid en passant square: {en_passant!r}")

    if not halfmove.isdigit():
        raise ValueError(f"halfmove clock must be a non-negative integer: {halfmove!r}")

    if not fullmove.isdigit() or int(fullmove) < 1:
        raise ValueError(f"fullmove number must be a positive integer: {fullmove!r}")

    return FenPosition(
        board=board,
        active_color=active_color,
        castling_rights=castling_rights,
        en_passant_square=en_passant_square,
        halfmove_clock=int(halfmove),
        fullmove_number=int(fullmove),
    )


def to_fen(position: FenPosition) -> str:
    placement = _serialize_placement(position.board)
    castling = _serialize_castling(position.castling_rights)
    en_passant = position.en_passant_square or "-"
    return (
        f"{placement} {position.active_color} {castling} {en_passant} "
        f"{position.halfmove_clock} {position.fullmove_number}"
    )


def _parse_placement(placement: str) -> tuple:
    ranks = placement.split("/")
    if len(ranks) != 8:
        raise ValueError(
            f"piece placement must have 8 ranks separated by '/': {placement!r}"
        )

    board = [None] * 64
    for rank_from_top, rank_str in enumerate(ranks):
        rank_index = 7 - rank_from_top
        file_index = 0
        for char in rank_str:
            if char.isdigit():
                skip = int(char)
                if skip < 1:
                    raise ValueError(f"invalid empty-square count in rank: {rank_str!r}")
                file_index += skip
            elif char in _PIECE_LETTERS:
                if file_index > 7:
                    raise ValueError(f"rank has too many squares: {rank_str!r}")
                board[rank_index * 8 + file_index] = char
                file_index += 1
            else:
                raise ValueError(f"invalid character in piece placement: {char!r}")
        if file_index != 8:
            raise ValueError(f"rank does not sum to 8 files: {rank_str!r}")

    return tuple(board)


def _serialize_placement(board) -> str:
    if len(board) != 64:
        raise ValueError(f"board must have exactly 64 squares, got {len(board)}")

    ranks = []
    for rank_index in range(7, -1, -1):
        rank_str = ""
        empty_count = 0
        for file_index in range(8):
            piece = board[rank_index * 8 + file_index]
            if piece is None:
                empty_count += 1
                continue
            if piece not in _PIECE_LETTERS:
                raise ValueError(f"invalid piece letter: {piece!r}")
            if empty_count:
                rank_str += str(empty_count)
                empty_count = 0
            rank_str += piece
        if empty_count:
            rank_str += str(empty_count)
        ranks.append(rank_str)
    return "/".join(ranks)


def _parse_castling(castling: str) -> CastlingRights:
    if castling == "-":
        return CastlingRights(False, False, False, False)

    valid_chars = set("KQkq")
    if not castling or set(castling) - valid_chars or len(set(castling)) != len(castling):
        raise ValueError(f"invalid castling availability: {castling!r}")

    return CastlingRights(
        white_kingside="K" in castling,
        white_queenside="Q" in castling,
        black_kingside="k" in castling,
        black_queenside="q" in castling,
    )


def _serialize_castling(rights: CastlingRights) -> str:
    letters = ""
    if rights.white_kingside:
        letters += "K"
    if rights.white_queenside:
        letters += "Q"
    if rights.black_kingside:
        letters += "k"
    if rights.black_queenside:
        letters += "q"
    return letters or "-"
