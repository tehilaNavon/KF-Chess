"""Canonical message type names for the wire protocol.

Kept in one place so client and server always agree on the strings.
"""

from __future__ import annotations


class ClientMessage:
    """Messages sent from client to server."""

    REGISTER = "REGISTER"
    LOGIN = "LOGIN"
    JOIN_GAME = "JOIN_GAME"
    COMMAND = "COMMAND"
    JUMP = "JUMP"


class ServerMessage:
    """Messages sent from server to client."""

    AUTH_OK = "AUTH_OK"
    AUTH_ERR = "AUTH_ERR"
    ERROR = "ERROR"
    SEATED = "SEATED"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    MOVE_REJECTED = "MOVE_REJECTED"
    GAME_OVER = "GAME_OVER"
