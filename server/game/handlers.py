"""Glue between the wire protocol and the live game.

Single concern: translate JOIN_GAME / COMMAND messages into LiveGame calls and
reply. No game rules, no engine access of its own.
"""

from __future__ import annotations

from server.dispatcher import Dispatcher
from server.game.live_game import LiveGame
from server.protocol.command_parser import parse_square
from server.protocol.messages import ClientMessage, ServerMessage
from server.session import Session

ERROR_BAD_SQUARE = "BAD_SQUARE"


def register_game_handlers(dispatcher: Dispatcher, game: LiveGame) -> None:
    async def handle_join(session: Session, payload: dict) -> None:
        if not session.is_authenticated:
            await session.send(ServerMessage.ERROR, error="NOT_AUTHENTICATED")
            return
        role = game.assign_seat(session)
        await session.send(
            ServerMessage.SEATED,
            role=role,
            color=game.color_of(session),
        )
        await session.send(ServerMessage.STATE_SNAPSHOT, **game.snapshot())

    async def handle_command(session: Session, payload: dict) -> None:
        ok, info = await game.apply_command(session, payload.get("cmd", ""))
        if not ok:
            await session.send(ServerMessage.MOVE_REJECTED, reason=info)

    async def handle_jump(session: Session, payload: dict) -> None:
        source = parse_square(payload.get("square", ""))
        if source is None:
            await session.send(ServerMessage.MOVE_REJECTED, reason=ERROR_BAD_SQUARE)
            return
        ok, info = await game.apply_jump(session, source)
        if not ok:
            await session.send(ServerMessage.MOVE_REJECTED, reason=info)

    dispatcher.register(ClientMessage.JOIN_GAME, handle_join)
    dispatcher.register(ClientMessage.COMMAND, handle_command)
    dispatcher.register(ClientMessage.JUMP, handle_jump)
