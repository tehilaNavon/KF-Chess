from Game.piece_config import piece_code_to_asset_folder


def build_sprite_path(pieces_root, piece_code, state_name, frame_number=1):
    piece_folder = piece_code_to_asset_folder(piece_code)
    return (
        pieces_root
        / piece_folder
        / "states"
        / state_name
        / "sprites"
        / f"{frame_number}.png"
    )
