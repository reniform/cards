import os
from models.monster import MonsterTemplate
from models.player  import PlayerUnit
from termio.view    import TerminalView
from termio.color   import TCol
from .enums  import ManaType
from .combat import Attack

# Insubstantiating the player states.
player = PlayerUnit()
opponent = PlayerUnit()

attack_flamethrower = Attack("Flamethrower", 50, {ManaType.FIRE: 2})
attack_scratch      = Attack("Scratch", 20, {ManaType.COLORLESS: 1})

# Template cards
dbCard1 = MonsterTemplate('Insipid Atom',   50, 20, [attack_flamethrower])
dbCard2 = MonsterTemplate('Petulant Beast', 50, 10, [attack_scratch])

dbCard3 = MonsterTemplate('Crotchety Ion', 150, 10, [attack_scratch])
dbCard4 = MonsterTemplate('Querulous Photon', 120, 20, [attack_flamethrower])

# Temporary setting activity
player.add_to_hand(dbCard1)
player.add_to_field(dbCard3)
player.set_active_monster(0)

opponent.add_to_hand(dbCard2)
opponent.set_active_monster(0)

def main():
    """
    The main() function is executed in main.py.
    """
    turn_count = 0
    while True:
        #TODO Buggy turn counter
        turn_count += 1
        print(f'{TCol.HEADER} Turn {turn_count} {TCol.ENDC}')
        print(TerminalView.get_player_status_string(player))
        print(TerminalView.get_player_status_string(opponent))
        command = input("What will you do? :D ")
        # RUN INPUT TURN
        match command.split():
            case ['attack']:
                player.active_monster.use_attack(0, player, opponent)
            case ['mana', manaType]:
                #TODO: If mana add fails or is invalid, handle the call here.
                player.add_mana(manaType, 1)
            case ['mana', manaType, qty]:
                player.add_mana(manaType, int(qty))
            case ['debug']:
                break
            case ["exit"]:
                print("Okay.")
                os._exit(1)
            case _:
                turn_count -= 1
                print("??? What???")
        
        # PERFORM CHECKS
        if opponent.active_monster.health <= 0:
            print("You win!")
            os._exit(1)