from abc import ABC, abstractmethod
import logging
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
        self.condition = kwargs.get("condition")
        self.execution_order = kwargs.get("execution_order")
        self._raw_data = kwargs

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
        # Get the effect_name str from the dict, which matches the DB column
        effect_name = effect_dict.get("effect_name")
        # Get the effect_class from the _effects list
        effect_class = cls._effects.get(effect_name)
        if not effect_class:
            logger.warning(f"Unknown effect name '{effect_name}' encountered. Skipping.")
            return None
        return effect_class(**effect_dict)


@EffectRegistry.register("draw_from_deck")
class DrawEffect(Effect):
    """
    `DrawEffect` (corresponding registration string: `draw_from_deck`)
    produces a drawn card in the player.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.amount = self.value or 1  # Use 'value' from DB

    def execute(self, game_state, source_card, target_player):
        target_player.draw_from_deck(self.amount)
        # no return: player modified directly

@EffectRegistry.register("APPLY_STATUS")
class ApplyStatusEffect(Effect):
    pass