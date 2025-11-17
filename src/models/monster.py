from core.enums import CardType, ManaType
from core.combat import Attack
from .card import CardTemplate

class MonsterTemplate(CardTemplate):
    """
    Immutable instance and static data source for monster cards. Holds the following values:
    ### Basic metadata
    * `title`: Monster name.
    * `health`: Hit points for the monster; maximum health is displayed with `max_health`.
    ### Play data
    * `attacks`: A list of attack-like actions to be taken by the monster in play. They are of type `Attack`, and may be chained with effects.
    """
    type = CardType.MONSTER
    id = None

    def __init__(self, **kwargs):
        # Recieve CardTemplate ID
        super().__init__()

        # Perform insubstantiation to necessary fields from kwargs.
        self.type           = kwargs['type']            # CardType
        self.title          = kwargs['title']           # str
        self.stage          = kwargs['stage']           # StageType
        self.mana_type      = kwargs['mana_type']       # ManaType
        self.evolve_from    = kwargs['evolve_from']     # str ?
        self.evolve_to      = kwargs['evolve_to']       # str ?
        self.health         = kwargs['health']          # int
        self.weak_type      = kwargs['weak_type']       # ManaType
        self.weak_mult      = kwargs['weak_mult']       # int
        self.resist_type    = kwargs['resist_type']     # ManaType
        self.resist_val     = kwargs['resist_val']      # int
        self.retreat_val    = kwargs['retreat_val']     # int
        self.attacks        = [Attack(**atk_data) for atk_data in kwargs['attacks']]

        # Perform insubstantiation to optional fields from kwargs.
        self.abilities      = kwargs['abilities']       # list: Ability
        self.level          = kwargs['level']           # int
        self.dex_data       = kwargs['dex_data']        # dict: JSON-esque
        self.print_data     = kwargs['print_data']      # dict: JSON-esque

class MonsterCard(CardTemplate):
    """
    Active and mutable instance of a monster card, instantiated from a `MonsterTemplate`.
    """

    def __init__(self, card):
        super().__init__()
        self.card = card
        self.id = card.id
        self.title = card.title
        self.health = self.card.health
        self.mana_pool = {mana_type: 0 for mana_type in ManaType}

    def use_attack(self, attack_index, player, target):
        """Performs attack from the given index. Attacks are listed (right now) in a list
        (though a dict would be better hahe).
        
        :param attack_index: The attack to be performed in the list.
        :param player: The performer of the attack.
        :param target: The target of the attack.
        """
        if 0 <= attack_index < len(self.card.attacks):
            attack = self.card.attacks[attack_index]
            attack.execute(player, target)
            return True
        else:
            print(f"Invalid attack index: {attack_index}. {self.card.title} does not have an attack at that position.")
            return False
    
    def take_damage(self, damage):
        """
        Reduces the monster's health by the given amount.
        """
        self.health -= damage

    #! MANA METHODS
    def has_mana(self, cost):
        """
        Checks whether there is sufficent mana in the mana pool for performing
        an action that costs mana.

        :param cost: is the attack's cost—usually a dict like `{ManaType.FIRE: 2, ...}`
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
    
    def spend_mana(self, cost):
        """
        Spends mana during the exertion of a move that costs a specific quantity of mana.

        :param cost: Mana quantity, expressed in a dict like `{ManaType.FIRE: 2, ...}`, to be subtracted from the monster's mana pool.
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
        