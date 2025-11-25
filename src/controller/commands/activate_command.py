from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState


class ActivateCommand(Command):
    """
    ACTIVATE sets a basic monster from the player's hand as the active monster.
    """

    def __init__(self, card_id: int):
        """
        Initializes the `ActivateCommand` object.

        Args:
            card_id (int): The unique ID of the monster card to activate.
        """
        self.card_id = card_id

    def execute(self, game_state: "GameState") -> tuple[bool, bool]:
        """
        Executes the ACTIVATE action.

        This moves a basic monster from the player's hand to their active monster
        slot. This action does not end the turn.

        Returns:
            A tuple `(False, True)` indicating the turn has not ended but the
            view needs to be redrawn.
        """
        player = game_state.current_player
        player.set_active_monster(self.card_id)
        return (False, True)
