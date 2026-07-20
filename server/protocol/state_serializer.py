"""Turn the live engine state into a plain dict for the wire.

Single concern: read-only projection of the engine into JSON-friendly data. It
never mutates anything.
"""

from __future__ import annotations


def serialize_game(adapter) -> dict:
    board = adapter.board
    engine = adapter.engine
    arbiter = engine.realtime_arbiter
    return {
        "grid": [list(row) for row in board.grid],
        "time": engine.current_time,
        "game_over": engine.is_game_over,
        "motions": [_serialize_motion(m) for m in arbiter.active_motions],
        "jumps": [_serialize_jump(j) for j in arbiter.active_jumps],
        "rests": _serialize_rests(arbiter),
    }


def _serialize_rests(arbiter) -> list:
    registry = arbiter.piece_rest_registry
    return [
        {"cell": [key[0], key[1]], "state": record.rest_state_name, "until": record.rest_until_time}
        for key, record in registry._rest_by_position.items()
    ]


def _serialize_motion(motion) -> dict:
    return {
        "source": [motion.source.row, motion.source.col],
        "destination": [motion.destination.row, motion.destination.col],
        "arrival_time": motion.arrival_time,
        "piece": motion.piece_code,
    }


def _serialize_jump(jump: dict) -> dict:
    return {
        "cell": [jump["cell"].row, jump["cell"].col],
        "start_time": jump["start_time"],
        "end_time": jump["end_time"],
        "piece": jump["piece_code"],
    }
