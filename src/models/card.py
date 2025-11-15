class CardTemplate:
    """
    Superclass for all cards, for
    * assigning a unique ID to each subclass card object, and;
    * creating a list that keeps track of all cards active in the game field.
    """
    _next_id = 0
    _all_cards = {}

    def __init__(self):
        """
        Initializes a new card instance; assigns the card ID; adds to central registry.
        """

        # Assign the next available unique ID to this card instance
        self.id = CardTemplate._next_id
        CardTemplate._next_id += 1

        # Add this new card instance to the central registry.
        CardTemplate._all_cards[self.id] = self

        # Increment the class-level counter for the next card.
        CardTemplate._next_id += 1
        
    @classmethod
    def get_card_by_id(cls, card_id):
        """
        Retrieves a card instance from the registry by its unique ID.

        :param card_id: The unique integer ID of the card.
        :return: The card object, or None if not found.
        """
        return cls._all_cards.get(card_id)

    @classmethod
    def get_all_cards(cls):
        """
        Returns a list of all card instances ever created.
        """
        return list(cls._all_cards.values())

    def __repr__(self):
        """
        Provides a developer-friendly string representation of the card.
        """
        # Attempts to find a 'title' attribute for a more descriptive name
        name = getattr(self, 'title', self.__class__.__name__)
        return f"<{name} (ID: {self.id})>"
