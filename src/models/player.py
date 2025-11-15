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

    def __init__(self):
        self.mana_pool = {mana_type: 0 for mana_type in ManaType}
        self.field = []
        self.hand = []
        self.deck = []
        self.discard = []
        self.prize = []
        self.active_monster = None

    #! FIELD METHODS
    def add_to_field(self, card):
        if len(self.field) >= self.CONST_MAX_CARDS:
            print("Too many cards in deck!")
            return False
        self.field.append(MonsterCard(card))
        return True

    #! HAND METHODS
    def add_to_hand(self, card):
        self.hand.append(MonsterCard(card))

    def retrieve_hand(self, card_index):
        pass

    def check_in_hand(self):
        pass
    
    def remove_from_hand(self):
        pass

    #! DISCARD METHODS
    def add_to_discard(self):
        pass

    def retrieve_discard(self):
        pass

    def check_in_discard(self):
        pass

    def remove_from_discard(self):
        pass

    #! ACTIVE MONSTER METHODS
    def set_active_monster(self, card_in_hand):
        if self.hand[card_in_hand].type != CardType.MONSTER:
            return False
        self.active_monster = self.hand[card_in_hand]
        return True

    #! CHECK FOR MANA
    def has_mana(self, cost):
        """Checks whether there is sufficent mana in the mana pool for performing
        an action that costs mana. 'cost' is a dict like {ManaType.FIRE: 2, ...}
        """

        # Make a copy to not mutate original: what remains will be 
        remaining_pool = self.mana_pool.copy()

        # First, pay specific mana costs. Colorless costs are handled later
        for mana_type, amount in cost.items():
            if mana_type == ManaType.COLORLESS:
                continue
            if self.mana_pool.get(mana_type, 0) < amount:
                return False
            remaining_pool[mana_type] -= amount

        # Handle colorless costs
        if ManaType.COLORLESS in cost:
            total_remaining = sum(remaining_pool.values())
            if total_remaining < cost[ManaType.COLORLESS]:
                return False
        
        return True

    def add_mana(self, mana_type_str, qty):
        """Adds mana of a specific type to the player state, and catches an exception
        if an invalid mana type is typed.
        """
        try:
            mana_type = ManaType(mana_type_str.lower())
            self.mana_pool[mana_type] += qty
        except (KeyError, ValueError):
            # Let the caller handle the error message
            return False

    def spend_mana(self, cost):
        """Spends mana during the exertion of a move that costs a specific quantity of mana.
        """
        # Pay non-colorless costs first
        for mana_type, amount in cost.items():
            if mana_type == ManaType.COLORLESS:
                continue
            self.mana_pool[mana_type] -= amount
        
        # Pay colorless costs
        if ManaType.COLORLESS in cost:
            colorless_needed = cost[ManaType.COLORLESS]
            for mana_type in ManaType:
                if colorless_needed <= 0:
                    break
                available = self.mana_pool[mana_type]
                to_spend = min(available, colorless_needed)
                self.mana_pool[mana_type] -= to_spend
                colorless_needed -= to_spend
        