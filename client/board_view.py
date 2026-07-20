"""OpenCV board view. Single concern: drive the existing AnimatedBoardRenderer
from server snapshots and turn clicks into move commands.

It reconstructs a Board + arbiter from each snapshot and advances the clock
between snapshots so the real renderer animates movement. It holds no game
rules - the server validates every move.
"""

from __future__ import annotations

import time
from typing import Optional

import cv2

from board import Board
from client.remote_engine import RemoteEngine
from client.ws_client import WSClient
from constants import ASSETS_PIECES_ROOT
from Display.animation.frame_highlight import build_frame_highlight, with_selected_position
from Display.rendering.animated_board_renderer import AnimatedBoardRenderer
from Game.controller import Controller
from Game.piece_config import PieceConfigRegistry
from Game.realtime_arbiter import Motion, RealTimeArbiter
from models import Position
from server.protocol.messages import ServerMessage

WINDOW = "KungFu Chess"


def _empty_grid() -> list[list[str]]:
    return [["."] * 8 for _ in range(8)]


class BoardView:
    def __init__(self, client: WSClient, color: Optional[str]) -> None:
        self._client = client
        self._color = color
        self._game_over = False
        self._winner: Optional[str] = None
        self._winner_name: Optional[str] = None
        self._server_time = 0
        self._synced_at = time.monotonic()

        self._renderer = AnimatedBoardRenderer()
        self._renderer.set_piece_config_registry(
            PieceConfigRegistry(assets_root=ASSETS_PIECES_ROOT)
        )
        self._board = Board(_empty_grid())
        self._arbiter = RealTimeArbiter(assets_root=ASSETS_PIECES_ROOT)
        self._controller = Controller(self._board, RemoteEngine(client, self._board))

    def run(self) -> None:
        cv2.namedWindow(WINDOW)
        cv2.setMouseCallback(WINDOW, self._on_mouse)
        try:
            while True:
                self._drain_network()
                cv2.imshow(WINDOW, self._render())
                if cv2.waitKey(16) & 0xFF in (ord("q"), 27):
                    break
        finally:
            cv2.destroyAllWindows()
            self._client.close()

    # --- network -----------------------------------------------------------
    def _drain_network(self) -> None:
        while (message := self._client.poll(timeout=0)) is not None:
            self._handle(message)

    def _handle(self, message: dict) -> None:
        message_type = message["type"]
        payload = message.get("payload", {})
        if message_type == ServerMessage.STATE_SNAPSHOT:
            self._apply_snapshot(payload)
        elif message_type == ServerMessage.GAME_OVER:
            self._game_over = True
            self._winner = payload.get("winner")
            self._winner_name = payload.get("winner_name")
        elif message_type == ServerMessage.MOVE_REJECTED:
            print("move rejected:", payload.get("reason"))

    def _apply_snapshot(self, payload: dict) -> None:
        self._game_over = payload["game_over"]
        self._server_time = payload["time"]
        self._synced_at = time.monotonic()
        self._board.grid = [list(row) for row in payload["grid"]]
        self._arbiter = self._build_arbiter(
            payload["motions"], payload["jumps"], payload.get("rests", [])
        )

    @staticmethod
    def _build_arbiter(motions: list, jumps: list, rests: list) -> RealTimeArbiter:
        arbiter = RealTimeArbiter(assets_root=ASSETS_PIECES_ROOT)
        arbiter.active_motions = [
            Motion(
                Position(*motion["source"]),
                Position(*motion["destination"]),
                motion["arrival_time"],
                motion["piece"],
            )
            for motion in motions
        ]
        arbiter.active_jumps = [
            {
                "cell": Position(*jump["cell"]),
                "start_time": jump["start_time"],
                "end_time": jump["end_time"],
                "piece_code": jump["piece"],
                "piece_color": jump["piece"][0],
            }
            for jump in jumps
        ]
        for rest in rests:
            arbiter.piece_rest_registry.schedule_rest(
                Position(*rest["cell"]), rest["state"], 0, rest["until"]
            )
        return arbiter

    def _current_time(self) -> float:
        return self._server_time + (time.monotonic() - self._synced_at) * 1000

    # --- input -------------------------------------------------------------
    def _on_mouse(self, event, x, y, _flags, _param) -> None:
        """Route clicks straight into the existing Controller (pixel->cell,
        selection and move/jump routing all live there)."""
        if self._game_over or self._color is None:
            return
        if event == cv2.EVENT_LBUTTONDOWN:
            self._controller.handle_click(x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self._controller.selected = None
            self._controller.handle_jump(x, y)

    # --- rendering ---------------------------------------------------------
    def _render(self):
        current_time = self._current_time()
        highlight = with_selected_position(
            build_frame_highlight(self._board, self._arbiter, current_time),
            self._controller.selected,
        )
        canvas = self._renderer.render(
            self._board, self._arbiter, current_time, frame_highlight=highlight
        )
        image = self._to_bgr(canvas.img)
        if self._game_over:
            self._draw_game_over(image)
        return image

    def _draw_game_over(self, image) -> None:
        height, width = image.shape[:2]
        winner = self._winner_name or self._winner_label()
        lines = [("GAME OVER", 1.4), (f"Winner: {winner}", 1.0)]
        total_height = sum(self._text_size(text, scale)[1] + 20 for text, scale in lines)
        y = (height - total_height) // 2
        for text, scale in lines:
            text_width, text_height = self._text_size(text, scale)
            x = (width - text_width) // 2
            y += text_height
            self._draw_centered_line(image, text, x, y, scale)
            y += 20

    def _winner_label(self) -> str:
        return {"w": "White", "b": "Black"}.get(self._winner, "?")

    @staticmethod
    def _text_size(text: str, scale: float):
        (width, height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 3)
        return width, height

    @staticmethod
    def _draw_centered_line(image, text: str, x: int, y: int, scale: float) -> None:
        cv2.putText(
            image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 6, cv2.LINE_AA
        )
        cv2.putText(
            image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 255), 3, cv2.LINE_AA
        )

    @staticmethod
    def _to_bgr(image):
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        return image
