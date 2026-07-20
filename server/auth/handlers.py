"""Glue between the wire protocol and the auth service.

Single concern: translate REGISTER/LOGIN messages into AuthService calls and
turn the result into an AUTH_OK / AUTH_ERR reply. No SQL, no crypto here.
"""

from __future__ import annotations

from server.auth.service import AuthResult, AuthService
from server.dispatcher import Dispatcher
from server.protocol.messages import ClientMessage, ServerMessage
from server.session import Session


def register_auth_handlers(dispatcher: Dispatcher, service: AuthService) -> None:
    async def handle_register(session: Session, payload: dict) -> None:
        result = await service.register(
            payload.get("username", ""),
            payload.get("password", ""),
        )
        await _reply(session, result)

    async def handle_login(session: Session, payload: dict) -> None:
        result = await service.login(
            payload.get("username", ""),
            payload.get("password", ""),
        )
        await _reply(session, result)

    dispatcher.register(ClientMessage.REGISTER, handle_register)
    dispatcher.register(ClientMessage.LOGIN, handle_login)


async def _reply(session: Session, result: AuthResult) -> None:
    if result.ok and result.user is not None:
        session.authenticate(result.user)
        await session.send(
            ServerMessage.AUTH_OK,
            username=result.user.username,
            rating=result.user.rating,
        )
        return
    await session.send(ServerMessage.AUTH_ERR, error=result.error)
