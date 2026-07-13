from constants import EMPTY_CELL


class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return isinstance(other, Position) and self.row == other.row and self.col == other.col

    def __repr__(self):
        return f"Position(row={self.row}, col={self.col})"


# class Piece:
#     def __init__(self, token):
#         self.token = token
#         self.color = token[0] if token != EMPTY_CELL else None
#         self.kind = token[1] if token != EMPTY_CELL else None

#     @classmethod
#     def from_token(cls, token):
#         return cls(token) if token != EMPTY_CELL else None
