"""Parsing and rendering of Standard Algebraic Notation move text.

This deliberately works on the move string alone, with no board state. SAN
is ambiguous about legality (a parser can't tell "Nbd7" is legal without a
board), but it is not ambiguous about grammar: piece letter, optional
disambiguation, capture marker, target square, promotion, check/mate suffix
or a castle. That grammar is what gets parsed and re-rendered here, which is
enough to normalize move text or feed a downstream legality checker.
"""

import re
from dataclasses import dataclass

_SAN_PATTERN = re.compile(
    r"^(?P<piece>[KQRBN])?"
    r"(?P<from_file>[a-h])?"
    r"(?P<from_rank>[1-8])?"
    r"(?P<capture>x)?"
    r"(?P<to_square>[a-h][1-8])"
    r"(?:=(?P<promotion>[QRBN]))?$"
)


@dataclass(frozen=True)
class ParsedMove:
    piece: str
    to_square: str
    is_capture: bool
    from_file: str | None
    from_rank: str | None
    promotion: str | None
    is_check: bool
    is_checkmate: bool
    is_castle_kingside: bool
    is_castle_queenside: bool


def parse_san(move: str) -> ParsedMove:
    if not isinstance(move, str) or not move.strip():
        raise ValueError("move must be a non-empty string")

    core = move.strip()
    is_checkmate = core.endswith("#")
    is_check = is_checkmate or core.endswith("+")
    if is_check:
        core = core[:-1]

    castle_body = core.replace("0", "O")
    if castle_body in ("O-O", "O-O-O"):
        return ParsedMove(
            piece="K",
            to_square="",
            is_capture=False,
            from_file=None,
            from_rank=None,
            promotion=None,
            is_check=is_check and not is_checkmate,
            is_checkmate=is_checkmate,
            is_castle_kingside=castle_body == "O-O",
            is_castle_queenside=castle_body == "O-O-O",
        )

    match = _SAN_PATTERN.match(core)
    if match is None:
        raise ValueError(f"unparseable SAN move: {move!r}")

    return ParsedMove(
        piece=match.group("piece") or "P",
        to_square=match.group("to_square"),
        is_capture=match.group("capture") is not None,
        from_file=match.group("from_file"),
        from_rank=match.group("from_rank"),
        promotion=match.group("promotion"),
        is_check=is_check and not is_checkmate,
        is_checkmate=is_checkmate,
        is_castle_kingside=False,
        is_castle_queenside=False,
    )


def to_san(parsed: ParsedMove) -> str:
    if parsed.is_castle_kingside or parsed.is_castle_queenside:
        body = "O-O-O" if parsed.is_castle_queenside else "O-O"
    else:
        piece_part = "" if parsed.piece == "P" else parsed.piece
        from_part = (parsed.from_file or "") + (parsed.from_rank or "")
        capture_part = "x" if parsed.is_capture else ""
        promotion_part = f"={parsed.promotion}" if parsed.promotion else ""
        body = f"{piece_part}{from_part}{capture_part}{parsed.to_square}{promotion_part}"

    suffix = "#" if parsed.is_checkmate else ("+" if parsed.is_check else "")
    return body + suffix
