from effects.effects import EffectRegistry
from core.enums import CardType
from .card import CardTemplate

import logging

logger = logging.getLogger(__name__)


class UtilityTemplate:
    """
    Immutable instance and static data source for monster cards.

    Attributes:
        type (CardType): `UtilityCards` are all type `UTILITY`.
        title (str): Necessary. The name of the utility card.
        description (str): Necessary. The card's description, as printed on the card.
        effects (list): Necessary. A list of effects, each their own dictionary.
    """

    type = CardType.UTILITY

    def __init__(self, **kwargs) -> None:
        self.title = kwargs["title"]
        self.descrpition = kwargs["description"]
        self.effects = kwargs.get("effects", [])  # list: Effect


class UtilityCard(CardTemplate):
    """
    Active and mutable instance of a utility card, instantiated from a `UtilityTemplate`.\n
    A `UtilityCard` composes its classes through the data stored in a `UtilityTemplate` card.
    The`UtilityTemplate`s pull their card data, such as name, stage level, attacks, ability,
    and data, from dicts, and hold them for a `UtilityCard` to access. The way a `UtilityCard`
    accesses its parent's data is by pulling it from their `card` attribute (i.e., `card.id`.
    `card.mana_type`, `card_retreat_val`.)

    Attributes:
        card (UtilityTemplate): The card template that `UtilityCard`s refers to as a data source.
        health (int): The monster's live health, nominally expressed in multiples of 10.
        mana_pool (dict): Deprecated.
        attached_mana (dict): A container for attached mana cards, sorted by mana type.
        abilities (list): A list of abilities, drawn from the card template's ability data.
    """

    def __init__(self, card) -> None:
        # Receive unique ID from superclass
        super().__init__()
        self.card = card
        self.effects = [
            EffectRegistry.create_effect(effect_data)
            for effect_data in (card.effects or [])
            if EffectRegistry.create_effect(effect_data) is not None
        ]
        logger.debug(f"Initiate {self.card.type} card ({self.id} {self.card.title})")

    @property
    def title(self):
        """Returns the title from the card template."""
        return self.card.title
