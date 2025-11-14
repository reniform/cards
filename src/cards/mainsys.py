from enum import Enum

class ManaType(Enum):
    GRASS       = 'grass'
    FIRE        = 'fire'
    WATER       = 'water'
    LIGHTNING   = 'lightning'
    FIGHTING    = 'fighting'
    PSYCHIC     = 'psychic'
    DARKNESS    = 'darkness'
    METAL       = 'metal'
    DRAGON      = 'dragon'
    FAIRY       = 'fairy'
    COLORLESS   = 'colorless'

class GlobalMonCard:
    def __init__(self, name, health, strength):
        self.title = name
        self.health = health
        self.strength = strength
        self.attacks = []

class Attack:
    def __init__(self, name, damage, cost):
        # cost will be a dict of {ManaType: amount}
        self.name = name
        self.damage = damage
        self.cost = cost
    
    def execute(self, attacker, target):
        if not attacker.has_mana(self.cost):
            print(f"Not enough mana for {self.name}!")
            return
        
        attacker.spend_mana(self.cost)
        target.take_damage(self.damage)
        print(f"{self.name} dealt {self.damage} damage!")
        

class PlayerMonState(GlobalMonCard):
    """The current player state, derived from the mon card.
        Initializes with name, health, and strength (attack power) so far.
        A mana pool, initialized with all mana-type values, is generated.
    """
    def __init__(self, name, health, strength):
        super().__init__(name, health, strength)
        self.mana_pool = {mana_type: 0 for mana_type in ManaType}
        self.attacks = [
            Attack("Flamethrower", 50, {ManaType.FIRE: 2, ManaType.COLORLESS: 1}),
            Attack("Fire Blast", 100, {ManaType.FIRE: 4})
        ]

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

    def use_attack(self, attack_index, target):
        """Performs attack from the given index"""
        attack = self.attacks[attack_index]
        attack.execute(self, target)
        
    def print_mana_pool(self):
        """This strange, temporary function serves merely to test
        mana quantities."""
        for type in self.mana_pool:
            if self.mana_pool[ManaType(type)] != 0:
                print(str(ManaType(type).value[:1].upper()) + 
                      str(self.mana_pool[ManaType(type)]), end=" ")
        print("")
    
    def take_damage(self, damage):
        self.health -= damage

player = PlayerMonState('Insipid Atom', 50, 20)
opponent = PlayerMonState('Petulant Beast', 60, 5)

while True:
    print(f'{player.title} \t\t HP {player.health}')
    player.print_mana_pool()
    print(f'{opponent.title} \t\t HP {opponent.health}')
    command = input("What will you do? :D ")
    # RUN INPUT TURN
    match command.split():
        case ['attack']:
            player.use_attack(0, opponent)
        case ['mana', manaType]:
            player.add_mana(manaType, 0)
        case ['mana', manaType, qty]:
            player.add_mana(manaType, int(qty))
        case ['debug']:
            break
        case ["exit"]:
            print("Okay.")
            exit()
        case _:
            print("??? What???")
    
    # PERFORM CHECKS
    if opponent.health <= 0:
        print("You win!")
        exit()