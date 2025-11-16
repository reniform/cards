from cards.enums import CardType
from .card import CardTemplate

class ManaTemplate(CardTemplate):
    type = CardType.MANA
    def __init__(self, **kwargs):
        super().__init__()
        self.type = kwargs['type']
        self.title = kwargs['title']
        self.mana_type = kwargs['mana_type']
        self.mana_val = kwargs['mana_val']


class ManaCard(ManaTemplate):
    def __init__(self, card):
        self.card = card
        self.id = card.id
        self.title = card.title
        self.type = card.type