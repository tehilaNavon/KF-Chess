import unittest

from server.auth import elo, passwords
from server.auth.db import Database
from server.auth.service import (
    ERROR_INVALID_CREDENTIALS,
    ERROR_INVALID_INPUT,
    ERROR_USERNAME_TAKEN,
    AuthService,
)
from server.auth.users import UserStore


class TestPasswords(unittest.TestCase):
    def test_hash_is_verifiable(self):
        salt = passwords.generate_salt()
        digest = passwords.hash_password("secret", salt)
        self.assertTrue(passwords.verify_password("secret", salt, digest))

    def test_wrong_password_fails(self):
        salt = passwords.generate_salt()
        digest = passwords.hash_password("secret", salt)
        self.assertFalse(passwords.verify_password("wrong", salt, digest))

    def test_salt_changes_hash(self):
        digest_a = passwords.hash_password("secret", passwords.generate_salt())
        digest_b = passwords.hash_password("secret", passwords.generate_salt())
        self.assertNotEqual(digest_a, digest_b)


class TestElo(unittest.TestCase):
    def test_equal_ratings_expect_half(self):
        self.assertAlmostEqual(elo.expected_score(1200, 1200), 0.5)

    def test_win_against_equal_gains_half_k(self):
        self.assertEqual(elo.updated_rating(1200, 1200, elo.SCORE_WIN), 1216)

    def test_loss_against_equal_drops_half_k(self):
        self.assertEqual(elo.updated_rating(1200, 1200, elo.SCORE_LOSS), 1184)

    def test_delta_is_symmetric_for_equal_ratings(self):
        winner = elo.rating_delta(1200, 1200, elo.SCORE_WIN)
        loser = elo.rating_delta(1200, 1200, elo.SCORE_LOSS)
        self.assertEqual(winner, -loser)


class TestAuthService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = Database(":memory:")
        await self.db.connect()
        self.service = AuthService(UserStore(self.db))

    async def asyncTearDown(self):
        await self.db.close()

    async def test_register_creates_user_with_default_rating(self):
        result = await self.service.register("alice", "pass")
        self.assertTrue(result.ok)
        self.assertEqual(result.user.username, "alice")
        self.assertEqual(result.user.rating, elo.DEFAULT_RATING)

    async def test_register_rejects_duplicate_username(self):
        await self.service.register("bob", "pass")
        result = await self.service.register("bob", "other")
        self.assertFalse(result.ok)
        self.assertEqual(result.error, ERROR_USERNAME_TAKEN)

    async def test_register_rejects_short_input(self):
        result = await self.service.register("ab", "x")
        self.assertFalse(result.ok)
        self.assertEqual(result.error, ERROR_INVALID_INPUT)

    async def test_login_succeeds_with_correct_password(self):
        await self.service.register("carol", "pass")
        result = await self.service.login("carol", "pass")
        self.assertTrue(result.ok)
        self.assertEqual(result.user.username, "carol")

    async def test_login_fails_with_wrong_password(self):
        await self.service.register("dave", "pass")
        result = await self.service.login("dave", "nope")
        self.assertFalse(result.ok)
        self.assertEqual(result.error, ERROR_INVALID_CREDENTIALS)

    async def test_login_fails_for_unknown_user(self):
        result = await self.service.login("ghost", "pass")
        self.assertFalse(result.ok)
        self.assertEqual(result.error, ERROR_INVALID_CREDENTIALS)


if __name__ == "__main__":
    unittest.main()
