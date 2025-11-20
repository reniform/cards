from core.enums import CardType
from .card import CardTemplate


class ManaTemplate:
    type = CardType.MANA

    def __init__(self, **kwargs):
        self.type = kwargs["type"]
        self.title = kwargs["title"]
        self.mana_type = kwargs["mana_type"]
        self.mana_val = kwargs["mana_val"]


class ManaCard(CardTemplate):
    def __init__(self, card) -> None:
        # Receive unique ID from superclass
        super().__init__()  # self.id
        self.card = card

    @property
    def title(self):
        """Returns the title from the card template."""
        return self.card.title
