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

class LivePlayerMonCard(GlobalMonCard):
    def __init__(self, name, health, strength):
        super().__init__(name, health, strength)
        self.mana = 0
        self.mana_pool = { 
            ManaType.GRASS: 0, ManaType.FIRE: 0,
            ManaType.WATER: 0, ManaType.LIGHTNING: 0,
            ManaType.FIGHTING: 0, ManaType.PSYCHIC: 0,
            ManaType.DARKNESS: 0, ManaType.METAL: 0,
            ManaType.DRAGON: 0, ManaType.FAIRY: 0
        }

    def addMana(self, mana_type_str, qty):
        """Adds mana to the player state."""
        try:
            mana_type = ManaType(mana_type_str.lower())
            self.mana_pool[mana_type] += qty
        except (KeyError, ValueError):
            print(f"Invalid mana type: {mana_type_str}")

    def attack(self, target, cost = 1):
        # Perform mana check
        if self.mana < cost:
            print("Not enough mana!")
            return
        
        # Perform arithmetic
        target.health = target.health - self.strength
        self.mana = self.mana - cost

        # Display effects
        print(self.title, "attacks", target.title, 
              "and inflicts", self.strength, "HP damage")
        
    def printManaPool(self):
        for type in self.mana_pool:
            if self.mana_pool[ManaType(type)] != 0:
                print(str(ManaType(type).value[:1].upper()) + 
                      str(self.mana_pool[ManaType(type)]), end=" ")
        print("")

player = LivePlayerMonCard('Insipid Atom', 50, 20)
opponent = LivePlayerMonCard('Petulant Beast', 60, 5)

while True:
    print(f'{player.title} \t\t HP {player.health}')
    player.printManaPool()
    print(f'{opponent.title} \t\t HP {opponent.health}')
    command = input("What will you do? :D ")
    # RUN INPUT TURN
    match command.split():
        case ['attack']:
            player.attack(opponent)
        case ['mana', manaType]:
            player.addMana(manaType, 1)
        case ["exit"]:
            print("Okay.")
            exit()
        case _:
            print("??? What???")
    
    # PERFORM CHECKS
    if opponent.health <= 0:
        print("You win!")
        exit()