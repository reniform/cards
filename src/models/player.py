import random
from models.monster import MonsterCard
from core.enums import ManaType, CardType


class PlayerUnit:
    """
    'PlayerUnit' holds all player data as pertains to the active player state, including:
    played cards, cards in hand, deck cards, discard pile, and prize cards, among other states.

    ## Methods
    ### Hand-related:
    * `add_to_hand()` TODO:
    * `check_hand()` TODO:
    * `remove_from_hand()` TODO:
    ### Mana-related:
    * `has_mana(cost)` Perform mana requirement checks for mana-expending actions
    * `add_mana(mana_type_str, qty)` Adding mana to an overall mana count (TODO: Attach mana to monster cards)
    * `spend_mana(cost)` Spending mana whenever a mana-expending action is performed
    ### Action-related:
    * `set_active_monster(card)` Set a monster to the active position.
    * `use_attack(attack_index, target)` Perform an attack.
    ### Debug:
    * `print_mana_pool()` Print mana pool in the terminal debug output.
    """

    type = CardType.MONSTER
    CONST_MAX_CARDS = 60
    CONST_MAX_BENCH_CARDS = 5

    def __init__(self, title="Player"):
        self.title = title
        self.field = {}
        self.deck = {}
        self.hand = {}
        self.discard = {}
        self.bench = {}
        self.prize = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        self.score = len(self.prize)
        self.active_monster = None

    #! FIELD METHODS
    def add_to_field(self, card):
        """
        Adds a card to the general field. The *field* is the list of all cards in the specific player space, including the deck, the hand, the bench, etc.
        TODO: Move max card check to the deck methods.

        :param card: The card to be added.
        :return: `True` if the card was successfully added; `False` otherwise.
        """
        if len(self.field) >= self.CONST_MAX_CARDS:
            print("Too many cards in deck!")
            return False
        self.field[card.id] = card
        return True
    
    #! DECK METHODS
    def initialize_deck(self):
        """
        Populates the deck from the player's field of cards.
        Stops when the deck reaches the maximum allowed card count.
        """
        if self.deck:
            print("Deck is already initialized.")
            return

        for card_id, card in self.field.items():
            if len(self.deck) >= self.CONST_MAX_CARDS:
                break
            self.deck[card_id] = card

    def shuffle_deck(self):
        """
        Performs a shuffle of the deck using random.
        """
        # Perform a check for an initialized deck.
        if not self.deck:
            print("Deck is not initialized.")
            return
        
        # Convert the dictionary's items to a list for shuffling.
        deck_items = list(self.deck.items())
        random.shuffle(deck_items)

        # Recreate the deck as a new dictionary with the shuffled order.
        self.deck = dict(deck_items)

    def remove_from_deck(self, qty):
        """
        Removes and returns a specified number of cards from the deck.

        :param qty: The number of cards to be removed.
        """
        
        # Perform a check for an initialized deck.
        if not self.deck:
            print("Deck is not initialized.")
            return

        popped_cards = {}
        for i in range(qty):
            if not self.deck:
                print("Deck is empty.")
                break
            card_id, card = self.deck.popitem()
            popped_cards[card_id] = card
        return popped_cards

    #! HAND METHODS
    def add_to_hand(self, card):
        """
        Adds a card to the hand.

        :param card: The card object to be added.
        """
        self.hand[card.id] = card

    def retrieve_hand(self, card_index):
        pass

    def check_in_hand(self):
        pass

    def remove_from_hand(self, card_id):
        """
        Removes and returns a card from the hand by its ID.

        :param card_id: The card ID of the card to be removed from within the hand.
        """
        return self.hand.pop(card_id, None)
    
    #! DECK -> HAND
    def draw_from_deck(self, qty=1):
        """Draws a specified number of cards from the deck and adds them to the hand."""
        drawn_cards = self.remove_from_deck(qty)
        if not drawn_cards:
            return
        for card in drawn_cards.values():
            self.add_to_hand(card)

    #! DISCARD METHODS
    def add_to_discard(self, card):
        """
        Adds a card to the discard pile.
        TODO: Why does `add_to_discard()` take a Card? Should a `src` be specified?

        :param card: The card to be added. `add_to_hand()` retrieves the card's unique integer ID, by which it performs the operation.
        """
        self.discard[card.id] = card

    def retrieve_discard(self):
        pass

    def check_in_discard(self):
        pass

    def remove_from_discard(self):
        pass

    #! BENCH METHODS
    def add_to_bench(self, card_id):
        """
        Adds a card to the bench **from the hand**. To my understanding, cards should move always from the hand to the bench; this is why `add_to_bench` looks from within the hand.

        :param card_id: The card ID of the card to be added to the bench.
        :return: `True` if the card was successfully added to the bench; `False` otherwise.
        """
        # Check against limit on amount of bench cards
        if len(self.bench) >= self.CONST_MAX_BENCH_CARDS:
            print("Too many cards in bench!")
            return False

        # Perform the bench operation:
        card_to_bench = self.hand[card_id]
        self.bench[card_id] = card_to_bench
        self.remove_from_hand(card_id)
        return True

    def retrieve_bench(self):
        pass

    def check_in_bench(self):
        pass

    def remove_from_bench(self, card_id):
        """
        Removes and returns a card from the bench by its ID.

        :param card_id: The card ID of the card to be removed from within the bench.
        :return: The removed card through `pop()`.
        """
        return self.bench.pop(card_id, None)

    #! ACTIVE MONSTER METHODS
    def set_active_monster(self, card_id):
        """
        Sets the active monster in the player's `active_monster` variable. The active monster is the chief actor in the player space, and is called upon to perform actions.

        :param card_id: The card ID of the card to be set as the active monster.
        :return: `True` if the card was successfully set as the active monster; `False` otherwise.
        """
        if self.hand[card_id].card.type != CardType.MONSTER:
            return False
        self.active_monster = self.hand[card_id]
        self.remove_from_hand(card_id)
        return True

    #! CHECK FOR MANA

    def add_mana(self, target, mana_type_str, qty=1):
        """
        Adds mana of a specific type to the active monster, and catches an exception if an invalid mana type is typed.
        The captured exception should be handled by the caller.

        :param target: The target card upon which the mana will be added. A check is performed to see whether the target card is a monster.
        :param mana_type_str: String of the mana type, checked against the `ManaType` enum.
        :param qty: The amount of mana to be added; by default, 1.
        :return: `True` if the mana was successfully added; `False` otherwise.
        """
        if not isinstance(target, MonsterCard):
            print("Target is not a monster!")
            return False
        try:
            mana_type = ManaType(mana_type_str.lower())
            target.mana_pool[mana_type] += qty
            return True
        except (KeyError, ValueError):
            # Let the caller handle the error message
            return False
