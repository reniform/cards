from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState, GameController


class UseCommand(Command):
    """
    USE allows the usage of a utility card from the hand.
    """

    def __init__(self, card_id: int):
        """
        Initializes the UseCommand.

        Args:
            card_id: The unique ID of the utility card in the hand to use.
        """
        self.card_id = card_id

    def execute(self, game_state: "GameState", controller: "GameController") -> tuple[bool, bool]:
        """
        Executes the USE action.

        This plays a utility card from the player's hand, triggering its
        effects. This action does not end the turn.

        Returns:
            A tuple (False, True) indicating the turn has not ended but
            the view needs to be redrawn.
        """
        player = game_state.current_player
        player.use_utility_card(self.card_id, game_state, controller)
        return (False, True)
