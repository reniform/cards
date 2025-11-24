from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game import GameState
    from models.player import PlayerUnit


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

    @abstractmethod
    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: PlayerUnit,
    ):
        """Overriden in subclasses. Returns a modified game_state."""
        raise NotImplementedError
    
    def __repr__(self):
        return f"{self.__class__.__name__}(target={self.target}, value={self.value})"