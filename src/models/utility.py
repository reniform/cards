from cards.enums import CardType
from .card import CardTemplate

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
        # self.flavor = kwargs['flavor'] # Add these back as you define utility card data
        # self.effects = kwargs['effects']

class UtilityCard(UtilityTemplate):
    """
    Active and mutable instance of a utility card, instantiated from a `UtilityTemplate`.
    """
    def __init__(self, card):
        self.card = card
        self.id = card.id
        self.title = card.title
        self.type = card.type