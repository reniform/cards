from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import logging
from core.coins import coin

if TYPE_CHECKING:
    from core.game import GameState
    from models.player import PlayerUnit
    from controller.game_controller import GameController


logger = logging.getLogger(__name__)


class Effect(ABC):
    """
    Abstract base class for all effects in the game.
    """

    def __init__(self, **kwargs):
        """
        Initializes an Effect from a dictionary of data, usually from the database.
        """
        self.source_card_id = kwargs.get("source_card_id")
        self.effect_name = kwargs.get("effect_name")
        self.target = kwargs.get("target")
        self.value = kwargs.get("value")
        self.condition = kwargs.get("condition", "ALWAYS")
        self.execution_order = kwargs.get("execution_order")
        self._raw_data = kwargs

    def _check_attack_success(self, attack_dealt_damage: bool | None) -> bool:
        """Helper to check for ONLY_IF_ATTACK_SUCCESSFUL condition."""
        if self.condition == "ONLY_IF_ATTACK_SUCCESSFUL":
            # If the condition requires success, the flag must be True.
            # attack_dealt_damage can be None if the effect is not from an attack.
            return attack_dealt_damage is True
        # If the condition is not about attack success, it doesn't block execution.
        return True

    def should_execute(self, attack_dealt_damage: bool | None = None) -> bool:
        """
        Evaluates if the effect's condition is met.
        Handles coin flips internally if required by the condition.
        """
        condition = self.condition
        if not self._check_attack_success(attack_dealt_damage):
            return False

        if condition == "ALWAYS":
            # No coin flip needed, the effect always passes its check.
            return True

        if "ON_COIN_FLIP" in condition:
            # This condition requires a coin flip. Let's perform it.
            logger.info("Flipping a coin for effect...")
            is_heads = coin()

            if is_heads:
                logger.info("Coin is HEADS.")
                # The condition passes only if it was waiting for HEADS.
                return condition == "ON_COIN_FLIP_HEADS"
            else:  # is_tails
                logger.info("Coin is TAILS.")
                # The condition passes only if it was waiting for TAILS.
                return condition == "ON_COIN_FLIP_TAILS"

        logger.warning(f"Unknown or unhandled condition: '{condition}'. Defaulting to False.")
        return False

    @abstractmethod
    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: "PlayerUnit",
        attack_dealt_damage: bool | None = None,
        controller: "GameController" | None = None,
    ):
        """Overriden in subclasses. Returns a modified game_state."""
        raise NotImplementedError
    
    def __repr__(self):
        return f"{self.__class__.__name__}(target={self.target}, value={self.value})"