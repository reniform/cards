from typing import TYPE_CHECKING, Optional
import logging

from .base_command import Command
from core.enums import ManaType

if TYPE_CHECKING:
    from core.game import GameState

logger = logging.getLogger(__name__)


class ManaCommand(Command):
    """
    A debug command to add mana directly to a monster.
    """

    def __init__(self, mana_type: str, quantity: int, target_id: Optional[int] = None):
        """
        Initializes the ManaCommand.

        Args:
            target_id: The ID of the monster to add mana to. Defaults to the active monster if None.
            mana_type: The string name of the mana type (e.g., "fire").
            quantity: The amount of mana to add.
        """
        self.target_id = target_id
        self.mana_type = mana_type
        self.quantity = quantity

    def execute(self, game_state: "GameState") -> tuple[bool, bool]:
        """
        Finds the target monster and adds the specified mana.
        """
        target_monster = None
        if self.target_id is None:
            # Default to the current player's active monster
            target_monster = game_state.current_player.active_monster
        else:
            # Search all players for the specified target monster
            for p in [game_state.current_player, game_state.waiting_player]:
                if p.active_monster and p.active_monster.id == self.target_id:
                    target_monster = p.active_monster
                    break
                if self.target_id in p.bench:
                    target_monster = p.bench[self.target_id]
                    break
        
        if not target_monster:
            logger.warning(f"MANA command failed: Target monster not found.")
            return False, False

        try:
            mana_enum = ManaType(self.mana_type.lower())
            target_monster.mana_pool[mana_enum] += self.quantity
            logger.info(f"Added {self.quantity} {self.mana_type} mana to {target_monster.title} (ID: {self.target_id}).")
            return False, True # Doesn't end turn, needs redraw
        except ValueError:
            logger.error(f"MANA command failed: Invalid mana type '{self.mana_type}'.")
            return False, False