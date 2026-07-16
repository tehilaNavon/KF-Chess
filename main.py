# Repository URL: not configured in this workspace
# If a git remote origin exists, replace this comment with the repository URL.

from Display.app.interactive_game import run_interactive_game
from Display.starting_board import create_standard_starting_board


def run():
    run_interactive_game(board=create_standard_starting_board())


if __name__ == "__main__":
    run()
