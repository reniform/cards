from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

class Effect(ABC):
    """
    Abstract base class for all effects in the game.
    """

    def __init__(self, effect_dict):
        """
        Applies the effect to the target. Effects receive their data from a dict.
        """
        self.effect_type = effect_dict.get("effect_type")
        # target defaults to self
        self.target = effect_dict.get("target", "self")
        self._raw_data = effect_dict

    @abstractmethod
    def execute(self, game_state, source_card, target_player):
        """Overriden in subclasses. Returns a modified game_state."""
        raise NotImplementedError


class EffectRegistry:
    """Central registry mapping effect-type strings to Effect classes"""

    _effects: dict = {}

    @classmethod
    def register(cls, effect_type):
        """Decorator to register effect classes"""

        # Fill out the effect class by taking in the effect_type
        def wrapper(effect_class):
            cls._effects[effect_type] = effect_class
            return effect_class

        return wrapper

    @classmethod
    def create_effect(cls, effect_dict):
        """Factory method: dict -> Effect instance"""
        # Get the effect_type str from the dict
        effect_type = effect_dict.get("effect_type")
        # Get the effect_class from the _effects list
        effect_class = cls._effects.get(effect_type)
        if not effect_class:
            logger.warning(f"Unknown effect type '{effect_type}' encountered. Skipping.")
            return None
        return effect_class(effect_dict)


@EffectRegistry.register("draw_from_deck")
class DrawEffect(Effect):
    """
    `DrawEffect` (corresponding registration string: `draw_from_deck`)
    produces a drawn card in the player.
    """

    def __init__(self, effect_dict):
        super().__init__(effect_dict)
        self.amount = effect_dict.get("amount", 1)

    def execute(self, game_state, source_card, target_player):
        target_player.draw_from_deck(self.amount)
        # no return: player modified directly
