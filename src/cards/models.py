from .enums import ManaType, CardType

# MonsterTemplate   Base data -> insubstantiated MT object
#   ↓                   
# MonsterCard       Live card in playerspace (in deck, discard, party)

class MonsterTemplate:
    """
    **MonsterTemplate** holds base data.
    """
    type = CardType.MONSTER
    id   = 1
    def __init__(self, title, health, strength, attacks):
        self.title = title
        self.health = health
        self.strength = strength
        self.attacks = attacks

class MonsterCard(MonsterTemplate):
    """
    **MonsterCard** represents monster cards active in the player's deck.
    They are instantiated from the global data within a `MonsterTemplate`.
    """
    #def __init__(self, title, health, strength, attacks):
        #pass
        #super().__init__(title, health, strength, attacks)

    def __init__(self, card):
        self.card = card
        self.title = card.title
        self.health = card.health
        self.strength = card.strength
        self.attacks = card.attacks

    def use_attack(self, attack_index, player, target):
        """Performs attack from the given index"""
        attack = self.attacks[attack_index]
        attack.execute(player, target)
    
    def take_damage(self, damage):
        self.health -= damage

class UtilityTemplate:
    type = CardType.UTILITY

class UtilityCard(UtilityTemplate):
    pass

class ManaTemplate:
    type = CardType.MANA

class ManaCard(ManaTemplate):
    pass

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
    CONST_MAX_CARDS = 60

    def __init__(self):
        self.mana_pool = {mana_type: 0 for mana_type in ManaType}
        self.field = []
        self.active_monster = None

    def add_to_field(self, card):
        if len(self.field) >= self.CONST_MAX_CARDS:
            print("Too many cards in deck!")
            return
        self.field.append(MonsterCard(card))
        print(f"{card.title} (id: {card.id}) added to field: {self.field}")

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
            print(f"Invalid mana type: {mana_type_str}")

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

    def set_active_monster(self, card_in_field):
        print(f"Activating {self.field[card_in_field]}")
        self.active_monster = self.field[card_in_field]
        print(f"Active monster set to {self.field[card_in_field]}")

    def print_mana_pool(self):
        """This strange, temporary function serves merely to test
        mana quantities."""
        for type in self.mana_pool:
            if self.mana_pool[ManaType(type)] != 0:
                print(str(ManaType(type).value[:2].upper()) + 
                      str(self.mana_pool[ManaType(type)]), end=" ")
        print("")

        