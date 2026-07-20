"""Server entrypoint: wires the bus, database, auth, dispatcher and transport."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

from server.auth.db import Database
from server.auth.handlers import register_auth_handlers
from server.auth.service import AuthService
from server.auth.users import UserStore
from server.bus import Bus
from server.dispatcher import Dispatcher
from server.game.handlers import register_game_handlers
from server.game.live_game import DEFAULT_SNAPSHOT_INTERVAL_MS, LiveGame
from server.transport.ws_server import ConnectionManager, websocket_handler

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "kungfu_chess.db"


def create_app(
    db_path: str = DEFAULT_DB_PATH,
    snapshot_interval_ms: int = DEFAULT_SNAPSHOT_INTERVAL_MS,
    move_time=None,
) -> FastAPI:
    bus = Bus()
    manager = ConnectionManager(bus)
    database = Database(db_path)
    auth_service = AuthService(UserStore(database))
    game = LiveGame(
        bus,
        move_time=move_time,
        snapshot_interval_ms=snapshot_interval_ms,
    )
    dispatcher = Dispatcher()
    register_auth_handlers(dispatcher, auth_service)
    register_game_handlers(dispatcher, game)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await database.connect()
        await game.start()
        logger.info("database ready at %s; game loop started", db_path)
        yield
        await game.stop()
        await database.close()

    app = FastAPI(title="KungFu Chess Server", lifespan=lifespan)
    app.state.bus = bus
    app.state.manager = manager
    app.state.database = database
    app.state.game = game

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "connections": manager.count}

    @app.websocket("/ws")
    async def ws(websocket: WebSocket) -> None:
        await websocket_handler(websocket, manager, dispatcher)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
