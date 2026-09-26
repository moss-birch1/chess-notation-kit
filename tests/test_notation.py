import unittest

from chess_notation import (
    CastlingRights,
    FenPosition,
    ParsedMove,
    index_to_square,
    is_valid_square,
    parse_fen,
    parse_san,
    square_color,
    square_to_index,
    to_fen,
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


class FenParsingTests(unittest.TestCase):
    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def test_starting_position_round_trip(self) -> None:
        position = parse_fen(self.STARTING_FEN)
        self.assertEqual(position.board[square_to_index("e1")], "K")
        self.assertEqual(position.board[square_to_index("e8")], "k")
        self.assertIsNone(position.board[square_to_index("e4")])
        self.assertEqual(position.active_color, "w")
        self.assertEqual(
            position.castling_rights,
            CastlingRights(True, True, True, True),
        )
        self.assertIsNone(position.en_passant_square)
        self.assertEqual(position.halfmove_clock, 0)
        self.assertEqual(position.fullmove_number, 1)
        self.assertEqual(to_fen(position), self.STARTING_FEN)

    def test_en_passant_and_partial_castling(self) -> None:
        fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w Kq d6 0 3"
        position = parse_fen(fen)
        self.assertEqual(position.en_passant_square, "d6")
        self.assertEqual(
            position.castling_rights,
            CastlingRights(True, False, False, True),
        )
        self.assertEqual(to_fen(position), fen)

    def test_no_castling_rights(self) -> None:
        fen = "8/8/8/4k3/8/8/8/4K3 b - - 12 34"
        position = parse_fen(fen)
        self.assertEqual(
            position.castling_rights,
            CastlingRights(False, False, False, False),
        )
        self.assertEqual(to_fen(position), fen)

    def test_wrong_field_count_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")

    def test_rank_not_summing_to_eight_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPP/RNBQKBNR w KQkq - 0 1")

    def test_bad_active_color_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_fen("8/8/8/8/8/8/8/8 x - - 0 1")

    def test_duplicate_castling_letter_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_fen("8/8/8/8/8/8/8/8 w KK - 0 1")

    def test_bad_en_passant_square_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_fen("8/8/8/8/8/8/8/8 w - z9 0 1")

    def test_non_numeric_move_counters_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_fen("8/8/8/8/8/8/8/8 w - - -1 1")
        with self.assertRaises(ValueError):
            parse_fen("8/8/8/8/8/8/8/8 w - - 0 0")

    def test_to_fen_is_pure_reconstruction(self) -> None:
        board = [None] * 64
        board[square_to_index("e1")] = "K"
        board[square_to_index("e8")] = "k"
        position = FenPosition(
            board=tuple(board),
            active_color="w",
            castling_rights=CastlingRights(False, False, False, False),
            en_passant_square=None,
            halfmove_clock=5,
            fullmove_number=10,
        )
        self.assertEqual(to_fen(position), "4k3/8/8/8/8/8/8/4K3 w - - 5 10")


if __name__ == "__main__":
    unittest.main()
