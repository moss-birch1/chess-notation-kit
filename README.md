# chess-notation-kit

Chess tools tend to bolt notation handling onto a board object: you can't get
`e4`'s index without instantiating a `Board`, and you can't check whether
`Nbd7` is syntactically well-formed without also asking whether it's legal.
Those are separate questions. This library only answers the notation
question, as plain functions over strings and integers, so it's easy to test
and easy to slot into whatever board or engine representation you're
actually using.

Three things live here so far:

- `chess_notation.squares` — converting between algebraic square names
  (`"e4"`) and the 0-63 index convention most engine protocols use, plus
  square color.
- `chess_notation.san` — parsing Standard Algebraic Notation move text
  (`"exd8=Q+"`, `"O-O"`) into a plain data record, and rendering that record
  back to text.
- `chess_notation.fen` — parsing Forsyth-Edwards Notation position strings
  into a plain data record, and rendering that record back to text.

No board state, no mutation, no third-party dependencies. Every public
function takes plain values in and returns plain values out.

## Usage

```python
from chess_notation import (
    square_to_index,
    index_to_square,
    square_color,
    parse_san,
    to_san,
)

square_to_index("e4")      # 28
index_to_square(28)        # "e4"
square_color("a1")         # "dark"

move = parse_san("exd8=Q+")
move.piece                 # "P"
move.from_file             # "e"
move.to_square             # "d8"
move.promotion             # "Q"
move.is_check              # True

to_san(move)                # "exd8=Q+"
```

Castling parses to the same record shape, with `piece` fixed at `"K"` and
`to_square` left empty since the destination isn't written in the move text:

```python
parse_san("O-O-O+").is_castle_queenside  # True
```

Invalid input raises `ValueError` rather than returning `None` or a partial
result, so callers don't have to guess what a missing field means.

FEN follows the same shape: a plain record in, a plain record out.

```python
from chess_notation import parse_fen, to_fen

position = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
position.board[square_to_index("e1")]   # "K"
position.active_color                   # "w"
position.castling_rights.white_kingside # True
position.en_passant_square              # None
position.fullmove_number                # 1

to_fen(position)  # "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
```

`board` is a 64-entry tuple indexed the same way as `square_to_index`, holding
either `None` or a piece letter (uppercase for white, lowercase for black).

## Installing

There's no package published yet. Clone the repo and install it locally in
editable mode:

```
pip install -e .
```

## Running the tests

```
python -m unittest
```

## Status

Early skeleton. Square conversion, SAN parsing/rendering, and FEN
parsing/rendering work and are covered by tests; UCI-style move notation
isn't implemented yet.
