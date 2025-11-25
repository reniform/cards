from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState, GameController


class RetreatCommand(Command):
    """
    RETREAT moves the active monster to the bench and promotes another.
    """

    def __init__(self, promoted_card_id: int):
        """
        Initializes the `RetreatCommand` object.

        Args:
            promoted_card_id: The unique ID of the benched monster to promote to the active spot.
        """
        self.promoted_card_id = promoted_card_id

    def execute(self, game_state: "GameState", controller: "GameController") -> tuple[bool, bool]:
        """
        Executes the RETREAT action.

        This swaps the active monster with a benched monster after paying
        the retreat cost. This action ends the player's turn.

        Returns:
            A tuple (True, True) indicating the turn has ended and the view
            needs to be redrawn.
        """
        player = game_state.current_player
        player.retreat_active_monster(self.promoted_card_id)
        return (True, True)
