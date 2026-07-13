# Repository URL: not configured in this workspace
# If a git remote origin exists, replace this comment with the repository URL.

from parser import parse_input
from validator import validate
from Game.game import Game


def run():
    board, commands = parse_input()
    error = validate(board)
    if error:
        print(error)
    else:
        game = Game(board)
        for command in commands:
            game.apply_command(command)


if __name__ == "__main__":
    run()
