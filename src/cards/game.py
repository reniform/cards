import os
from models.monster import MonsterTemplate
from models.player  import PlayerUnit
from termio.view    import TerminalView
from termio.termio  import CommandHandler
from termio.color   import TCol
from .enums  import ManaType
from .combat import Attack
from ...data.testpy.carddata import *

# Insubstantiating the player states.
player = PlayerUnit()
opponent = PlayerUnit()

attack_flamethrower = Attack("Flamethrower", 50, {ManaType.FIRE: 2}, None)
attack_scratch      = Attack("Scratch", 20, {ManaType.COLORLESS: 1}, None)

# Template cards
dbCard1 = MonsterTemplate('Insipid Atom', 50, [attack_flamethrower])
dbCard2 = MonsterTemplate('Petulant Beast', 50, [attack_scratch])

dbCard3 = MonsterTemplate('Crotchety Ion', 150, [attack_scratch])
dbCard4 = MonsterTemplate('Querulous Photon', 120, [attack_flamethrower])

# Temporary setting activity
player.add_to_hand(dbCard1)
player.add_to_hand(dbCard3)
player.set_active_monster(0)

opponent.add_to_hand(dbCard2)
opponent.set_active_monster(1)

def main():
    """
    The main() function is executed in main.py.
    """
    turn_count = 0
    while True:
        #TODO Buggy turn counter
        turn_count += 1
        print(f'{TCol.HEADER} Turn {turn_count} {TCol.ENDC}')
        print(TerminalView.get_player_status_string(opponent))
        print(TerminalView.get_player_status_string(player, bold=True))
        command = input("What will you do? :D ")

        parts = command.split()
        if not parts:
            turn_count -= 1
            continue

        command_word = parts[0]
        args = parts[1:]

        if command_word == 'debug': # Special case to break the loop
            break
        elif handler := CommandHandler.COMMANDS.get(command_word):
            handler(player, opponent, *args)
        else:
            turn_count -= 1
            print("??? What???")

        # PERFORM CHECKS
        if opponent.active_monster.health <= 0:
            print("You win!")
            os._exit(1)