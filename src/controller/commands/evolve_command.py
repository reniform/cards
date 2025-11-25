from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState, GameController


class EvolveCommand(Command):
    """
    EVOLVE evolves a monster on the field using a card from the hand.
    """

    def __init__(self, evo_card_id: int, base_card_id: int):
        """
        Initializes the `EvolveCommand` object.

        Args:
            evo_card_id: The unique ID of the evolution card in the hand.
            base_card_id: The unique ID of the monster on the field to evolve.
        """
        self.evo_card_id = evo_card_id
        self.base_card_id = base_card_id

    def execute(self, game_state: "GameState", controller: "GameController") -> tuple[bool, bool]:
        """
        Executes the EVOLVE action.

        This finds the evolution card in hand and the base monster on the field,
        then performs the evolution. This action does not end the turn.

        Returns:
            A tuple `(False, True)` indicating the turn has not ended but
            the view needs to be redrawn.
        """
        player = game_state.current_player
        player.evolve_monster(self.evo_card_id, self.base_card_id)
        return (False, True)
