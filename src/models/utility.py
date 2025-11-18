from effects.effects import EffectRegistry
from core.enums import CardType
from .card import CardTemplate

import logging
logger = logging.getLogger(__name__)

class UtilityTemplate(CardTemplate):
    """
    Immutable instance and static data source for monster cards. Holds the following values:
    ### Basic metadata
    * `title`: Name of the utility.
    * `flavor`: Description of the utility.
    * `effects`: A list of effects induced by the utility. They are of type `Effect`.
    """
    type = CardType.UTILITY

    def __init__(self, **kwargs):
        super().__init__()
        self.title = kwargs['title']
        self.effects = kwargs.get('effects', []) # list: Effect

class UtilityCard(CardTemplate):
    """
    Active and mutable instance of a utility card, instantiated from a `UtilityTemplate`.
    """
    def __init__(self, card):
        super().__init__()
        self.card = card
        self.id = card.id
        self.title = card.title
        self.type = card.type
        self.effects = [
            EffectRegistry.create_effect(effect_data)
            for effect_data in (card.effects or [])
            if EffectRegistry.create_effect(effect_data) is not None
        ]
        logger.debug(f"Initiate {self.type} card ({self.id} {self.title})")