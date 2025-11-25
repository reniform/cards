from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState

class PassCommand(Command):
    """
    PASS ends the current player's turn.
    """

    def __init__(self):
        pass

    def execute(self, game_state: 'GameState') -> tuple[bool, bool]:
        """
        Executes the PASS action.

        This command doesn't modify the game state directly. It only signals
        that the turn has ended. `GameController` recognizes the `True` value for
        `turn_ended` and will call `game_state.next_turn()`.

        Returns:
            A tuple `(True, True)` indicating that 1) the turn has ended, and 2)
            the view should be redrawn for the next player.
        """
        return (True, True)