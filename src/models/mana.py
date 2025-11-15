from cards.enums import CardType
from .card import CardTemplate

class ManaTemplate(CardTemplate):
    type = CardType.MANA

class ManaCard(ManaTemplate):
    pass