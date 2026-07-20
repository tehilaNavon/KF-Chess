import unittest

from server.bus import Bus
from server.game.live_game import (
    ERROR_NOT_A_PLAYER,
    ERROR_NOT_YOUR_COLOR,
    LiveGame,
)
from server.protocol.command_parser import ERROR_BAD_FORMAT
from server.session import ROLE_BLACK, ROLE_VIEWER, ROLE_WHITE, Session


def _make_session() -> Session:
    return Session(connection=None)


class TestSeating(unittest.TestCase):
    def setUp(self):
        self.game = LiveGame(Bus(), move_time=1000)

    def test_first_player_is_white(self):
        self.assertEqual(self.game.assign_seat(_make_session()), ROLE_WHITE)

    def test_second_player_is_black(self):
        self.game.assign_seat(_make_session())
        self.assertEqual(self.game.assign_seat(_make_session()), ROLE_BLACK)

    def test_third_player_is_viewer(self):
        self.game.assign_seat(_make_session())
        self.game.assign_seat(_make_session())
        self.assertEqual(self.game.assign_seat(_make_session()), ROLE_VIEWER)

    def test_color_of_roles(self):
        white = _make_session()
        self.game.assign_seat(white)
        self.assertEqual(self.game.color_of(white), "w")


class TestApplyCommand(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = LiveGame(Bus(), move_time=1000)
        self.white = _make_session()
        self.game.assign_seat(self.white)

    async def test_valid_move_is_accepted(self):
        ok, info = await self.game.apply_command(self.white, "WNb1c3")
        self.assertTrue(ok, info)

    async def test_moving_opponent_color_rejected(self):
        ok, reason = await self.game.apply_command(self.white, "bNb8c6")
        self.assertFalse(ok)
        self.assertEqual(reason, ERROR_NOT_YOUR_COLOR)

    async def test_bad_format_rejected(self):
        ok, reason = await self.game.apply_command(self.white, "nonsense")
        self.assertFalse(ok)
        self.assertEqual(reason, ERROR_BAD_FORMAT)

    async def test_viewer_cannot_move(self):
        self.game.assign_seat(_make_session())  # black
        viewer = _make_session()
        self.game.assign_seat(viewer)
        ok, reason = await self.game.apply_command(viewer, "WNb1c3")
        self.assertFalse(ok)
        self.assertEqual(reason, ERROR_NOT_A_PLAYER)


if __name__ == "__main__":
    unittest.main()
