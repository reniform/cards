from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState, GameController


class BenchCommand(Command):
    """
    BENCH moves a basic monster from a player's hand to an empty bench slot.
    """

    def __init__(self, card_id: int):
        """
        Initializes the `BenchCommand` object.

        Args:
            card_id: The unique ID of the monster card in the hand to bench.
        """
        self.card_id = card_id

    def execute(self, game_state: "GameState", controller: "GameController") -> tuple[bool, bool]:
        """
        Executes the BENCH action.

        This moves a basic monster from the player's hand to their bench.
        This action does not end the turn.

        Returns:
            A tuple `(False, True)` indicating the turn has not ended but
            the view needs to be redrawn.
        """
        player = game_state.current_player
        player.add_to_bench(self.card_id)
        return (False, True)
