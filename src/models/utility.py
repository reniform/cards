from cards.enums import CardType

class UtilityTemplate:
    """
    Immutable instance and static data source for monster cards. Holds the following values:
    ### Basic metadata
    * `title`: Name of the utility.
    * `flavor`: Description of the utility.
    * `effects`: A list of effects induced by the utility. They are of type `Effect`.
    """
    type = CardType.UTILITY
    id   = 100

    def __init__(self, title, flavor, effects):
        self.title = title
        self.flavor = flavor
        self.effects = effects

class UtilityCard(UtilityTemplate):
    """
    Active and mutable instance of a utility card, instantiated from a `UtilityTemplate`.
    """
    pass