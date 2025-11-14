import os
from .models import MonsterTemplate, PlayerUnit
from .enums  import ManaType
from .combat import Attack

# Insubstantiating the player states.
player = PlayerUnit()
opponent = PlayerUnit()

attack_flamethrower = Attack("Flamethrower", 50, {ManaType.FIRE: 2})
attack_scratch      = Attack("Scratch", 20, {ManaType.COLORLESS: 1})

# Template cards
dbCard1 = MonsterTemplate('Insipid Atom',   50, 20, [attack_flamethrower, attack_scratch])
dbCard2 = MonsterTemplate('Petulant Beast', 1200, 10, [attack_scratch])

# Temporary setting activity
player.add_to_field(dbCard1)
player.set_active_monster(0)

opponent.add_to_field(dbCard2)
opponent.set_active_monster(0)

def main():
    """
    The main() function is executed in main.py.
    """
    while True:
        print(f'{player.active_monster.title} \t\t HP {player.active_monster.health}')
        player.print_mana_pool()
        print(f'{opponent.active_monster.title} \t\t HP {opponent.active_monster.health}')
        command = input("What will you do? :D ")
        # RUN INPUT TURN
        match command.split():
            case ['attack']:
                player.active_monster.use_attack(0, player, opponent)
            case ['mana', manaType]:
                player.add_mana(manaType, 1)
            case ['mana', manaType, qty]:
                player.add_mana(manaType, int(qty))
            case ['debug']:
                break
            case ["exit"]:
                print("Okay.")
                os._exit(1)
            case _:
                print("??? What???")
        
        # PERFORM CHECKS
        if opponent.active_monster.health <= 0:
            print("You win!")
            exit()