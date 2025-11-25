from logging import getLogger
from .base_effect import Effect

logger = getLogger(__name__)


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
    def create_effect(cls, effect_dict: dict) -> Effect:
        """Factory method: dict -> Effect instance"""
        # Get the effect_name str from the dict, which matches the DB column
        effect_name = effect_dict.get("effect_name")
        # Get the effect_class from the _effects list
        effect_class = cls._effects.get(effect_name)
        if not effect_class:
            logger.warning(
                f"Unknown effect name '{effect_name}' encountered. Skipping."
            )
            return None
        return effect_class(**effect_dict)


# Import all effect modules here to ensure they are registered.
from . import monster_effects # noqa: E402, F401
from . import player_effects  # noqa: E402, F401
