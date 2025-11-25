from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState


class AttachCommand(Command):
    """
    ATTACH joins a mana card from the hand to a monster on the field.
    """

    def __init__(self, mana_card_id: int, target_id: int):
        """
        Initializes the `AttachCommand` object.

        Args:
            mana_card_id: The unique ID of the mana card in the hand.
            target_id: The unique ID of the monster to attach to.
        """
        self.mana_card_id = mana_card_id
        self.target_id = target_id

    def execute(self, game_state: "GameState") -> tuple[bool, bool]:
        """
        Executes the ATTACH action.

        This finds the mana card in the player's hand and the target monster
        on their field, then performs the attachment. This action does not
        end the turn.

        Returns:
            A tuple `(False, True)` indicating the turn has not ended but
            the view needs to be redrawn.
        """
        player = game_state.current_player
        player.attach_mana(self.mana_card_id, self.target_id)
        return (False, True)
