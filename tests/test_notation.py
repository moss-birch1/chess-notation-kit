import unittest

from chess_notation import (
    ParsedMove,
    index_to_square,
    is_valid_square,
    parse_san,
    square_color,
    square_to_index,
    to_san,
)


class SquareConversionTests(unittest.TestCase):
    def test_corner_squares(self) -> None:
        self.assertEqual(square_to_index("a1"), 0)
        self.assertEqual(square_to_index("h1"), 7)
        self.assertEqual(square_to_index("a8"), 56)
        self.assertEqual(square_to_index("h8"), 63)

    def test_round_trip_every_square(self) -> None:
        for index in range(64):
            square = index_to_square(index)
            self.assertEqual(square_to_index(square), index)

    def test_invalid_square_rejected(self) -> None:
        self.assertFalse(is_valid_square("i1"))
        self.assertFalse(is_valid_square("a9"))
        self.assertFalse(is_valid_square("a"))
        with self.assertRaises(ValueError):
            square_to_index("z9")

    def test_square_color(self) -> None:
        self.assertEqual(square_color("a1"), "dark")
        self.assertEqual(square_color("h1"), "light")
        self.assertEqual(square_color("h8"), "dark")


class SanParsingTests(unittest.TestCase):
    def test_pawn_push(self) -> None:
        parsed = parse_san("e4")
        self.assertEqual(parsed.piece, "P")
        self.assertEqual(parsed.to_square, "e4")
        self.assertFalse(parsed.is_capture)

    def test_pawn_capture(self) -> None:
        parsed = parse_san("exd5")
        self.assertEqual(parsed.piece, "P")
        self.assertEqual(parsed.from_file, "e")
        self.assertTrue(parsed.is_capture)
        self.assertEqual(parsed.to_square, "d5")

    def test_disambiguated_knight_move(self) -> None:
        parsed = parse_san("Nbd7")
        self.assertEqual(parsed.piece, "N")
        self.assertEqual(parsed.from_file, "b")
        self.assertIsNone(parsed.from_rank)
        self.assertEqual(parsed.to_square, "d7")

    def test_promotion_with_check(self) -> None:
        parsed = parse_san("exd8=Q+")
        self.assertEqual(parsed.promotion, "Q")
        self.assertTrue(parsed.is_check)
        self.assertFalse(parsed.is_checkmate)

    def test_checkmate_suffix(self) -> None:
        parsed = parse_san("Qh5#")
        self.assertTrue(parsed.is_checkmate)
        self.assertFalse(parsed.is_check)

    def test_castling(self) -> None:
        kingside = parse_san("O-O")
        self.assertTrue(kingside.is_castle_kingside)
        self.assertFalse(kingside.is_castle_queenside)

        queenside = parse_san("O-O-O+")
        self.assertTrue(queenside.is_castle_queenside)
        self.assertTrue(queenside.is_check)

    def test_rejects_garbage(self) -> None:
        with self.assertRaises(ValueError):
            parse_san("not a move")

    def test_round_trip(self) -> None:
        for move in ("e4", "exd5", "Nbd7", "exd8=Q+", "Qh5#", "O-O", "O-O-O+"):
            self.assertEqual(to_san(parse_san(move)), move)

    def test_to_san_is_pure_reconstruction(self) -> None:
        parsed = ParsedMove(
            piece="R",
            to_square="a3",
            is_capture=False,
            from_file=None,
            from_rank="1",
            promotion=None,
            is_check=False,
            is_checkmate=False,
            is_castle_kingside=False,
            is_castle_queenside=False,
        )
        self.assertEqual(to_san(parsed), "R1a3")


if __name__ == "__main__":
    unittest.main()
