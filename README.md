# chess-notation-kit

Chess tools tend to bolt notation handling onto a board object: you can't get
`e4`'s index without instantiating a `Board`, and you can't check whether
`Nbd7` is syntactically well-formed without also asking whether it's legal.
Those are separate questions. This library only answers the notation
question, as plain functions over strings and integers, so it's easy to test
and easy to slot into whatever board or engine representation you're
actually using.

Two things live here so far:

- `chess_notation.squares` — converting between algebraic square names
  (`"e4"`) and the 0-63 index convention most engine protocols use, plus
  square color.
- `chess_notation.san` — parsing Standard Algebraic Notation move text
  (`"exd8=Q+"`, `"O-O"`) into a plain data record, and rendering that record
  back to text.

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

Early skeleton. Square conversion and SAN parsing/rendering work and are
covered by tests; FEN and UCI-style move notation aren't implemented yet.
