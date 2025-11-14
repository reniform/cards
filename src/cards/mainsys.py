from enum import Enum

playMode = True

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
    
    def executeAttack(self, attacker, target):
        pass

class PlayerMonState(GlobalMonCard):
    """The current player state, derived from the mon card.
        Initializes with name, health, and strength (attack power) so far.
        A mana pool, initialized with all mana-type values, is generated.
    """
    def __init__(self, name, health, strength):
        super().__init__(name, health, strength)
        self.mana_pool = { 
            # Initialize pool with default values
            ManaType.GRASS: 0, ManaType.FIRE: 0,
            ManaType.WATER: 0, ManaType.LIGHTNING: 0,
            ManaType.FIGHTING: 0, ManaType.PSYCHIC: 0,
            ManaType.DARKNESS: 0, ManaType.METAL: 0,
            ManaType.DRAGON: 0, ManaType.FAIRY: 0,
            ManaType.COLORLESS: 0
        }

    def has_mana(self, cost):
        """Checks whether there is sufficent mana in the mana pool for performing
        an action that costs mana. 'cost' is a dict like {ManaType.FIRE: 2, ...}
        """
        for mana_type, amount in cost.items():
            if self.mana_pool.get(mana_type, 0) < amount:
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
        for mana_type, amount in cost.items():
            self.mana_pool[mana_type] -= amount

    def attack(self, target, mana_cost = 1):
        """Performs an 'attack' move that depletes the health of an opponent.
        First, a mana check is performed, testing whether the player has sufficient mana in the mana pool.
        Second, arithmetic is performed: the target sustains damage, and the mana is removed from the mana pool.
        The effects are then displayed.
        """
        # Perform mana check
        if not self.has_mana(mana_cost):
            print("Not enough mana!")
            return
        
        # Perform arithmetic
        target.health = target.health - self.strength
        self.spend_mana(mana_cost)

        # Display effects
        print(self.title, "attacks", target.title, 
              "and inflicts", self.strength, "HP damage")
        
    def printManaPool(self):
        """This strange, temporary function serves merely to test
        mana quantities."""
        for type in self.mana_pool:
            if self.mana_pool[ManaType(type)] != 0:
                print(str(ManaType(type).value[:1].upper()) + 
                      str(self.mana_pool[ManaType(type)]), end=" ")
        print("")

player = PlayerMonState('Insipid Atom', 50, 20)
opponent = PlayerMonState('Petulant Beast', 60, 5)

while True:
    print(f'{player.title} \t\t HP {player.health}')
    player.printManaPool()
    print(f'{opponent.title} \t\t HP {opponent.health}')
    command = input("What will you do? :D ")
    # RUN INPUT TURN
    match command.split():
        case ['attack']:
            player.attack(opponent, {ManaType.FIRE: 2, ManaType.COLORLESS: 1})
        case ['mana', manaType]:
            player.add_mana(manaType, 1)
        case ["exit"]:
            print("Okay.")
            exit()
        case _:
            print("??? What???")
    
    # PERFORM CHECKS
    if opponent.health <= 0:
        print("You win!")
        exit()