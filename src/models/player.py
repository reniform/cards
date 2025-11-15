from cards.enums import ManaType, CardType
from .monster import MonsterCard
# Waiting upon utility and mana definitions.
#from .utility import UtilityCard
#from .mana import ManaCard


class PlayerUnit():
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

    def __init__(self):
        self.field = {}
        self.deck = {}
        self.hand = {}
        self.discard = {}
        self.prize = {}
        self.bench = {}
        self.active_monster = None

    #! FIELD METHODS
    def add_to_field(self, card):
        """
        Adds a card to the general field.
        :param card: The card to be added.
        :return: True if the card was successfully added, False otherwise.
        """
        if len(self.field) >= self.CONST_MAX_CARDS:
            print("Too many cards in deck!")
            return False
        self.field[card.id] = MonsterCard(card)
        return True

    #! HAND METHODS
    def add_to_hand(self, card):
        self.hand[card.id] = MonsterCard(card)

    def retrieve_hand(self, card_index):
        pass

    def check_in_hand(self):
        pass
    
    def remove_from_hand(self, card_id):
        """
        Removes and returns a card from the hand by its ID.
        """
        return self.hand.pop(card_id, None)


    #! DISCARD METHODS
    def add_to_discard(self):
        pass

    def retrieve_discard(self):
        pass

    def check_in_discard(self):
        pass

    def remove_from_discard(self):
        pass

    #! BENCH METHODS
    def add_to_bench(self, card_id):
        """
        Adds a card to the bench **from the hand**.
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
        """
        return self.bench.pop(card_id, None)

    #! ACTIVE MONSTER METHODS
    def set_active_monster(self, card_id):
        if self.hand[card_id].type != CardType.MONSTER:
            return False
        self.active_monster = self.hand[card_id]
        self.remove_from_hand(card_id)
        return True

    #! CHECK FOR MANA

    def add_mana(self, target, mana_type_str, qty):
        """Adds mana of a specific type to the active monster, and catches an exception
        if an invalid mana type is typed.
        """
        try:
            mana_type = ManaType(mana_type_str.lower())
            target.mana_pool[mana_type] += qty
        except (KeyError, ValueError):
            # Let the caller handle the error message
            return False