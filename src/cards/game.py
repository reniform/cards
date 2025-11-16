import os
from cards.enums    import CardType
from models.monster import MonsterTemplate, MonsterCard
from models.utility import UtilityTemplate, UtilityCard
from models.mana    import ManaTemplate, ManaCard
from models.player  import PlayerUnit
from termio.view    import TerminalView
from termio.termio  import CommandHandler
import colorful as cf
from .carddata import give_test_card

# Insubstantiating the player states.
player = PlayerUnit()
opponent = PlayerUnit('Opponent')

#attack_flamethrower = Attack("Flamethrower", 50, {ManaType.FIRE: 2}, None)
#attack_scratch      = Attack("Scratch", 20, {ManaType.COLORLESS: 1}, None)

# Template cards
#dbCard1 = MonsterTemplate('Insipid Atom', 50, [attack_flamethrower])
#dbCard2 = MonsterTemplate('Petulant Beast', 50, [attack_scratch])

#dbCard3 = MonsterTemplate('Crotchety Ion', 150, [attack_scratch])
#dbCard4 = MonsterTemplate('Querulous Photon', 120, [attack_flamethrower])

c1 = MonsterCard(MonsterTemplate(**give_test_card(3)))
c2 = MonsterCard(MonsterTemplate(**give_test_card(1)))

# Temporary setting activity
#player.add_to_hand(c1)
#player.set_active_monster(0)
#opponent.add_to_hand(c2)
#opponent.set_active_monster(1)

def generate_deck_from_list(deck_list, player_unit):
    for card in deck_list:
        match card['type']:
            case CardType.MONSTER:
                player_unit.add_to_field(MonsterCard(MonsterTemplate(**card)))
            case CardType.UTILITY:
                player_unit.add_to_field(UtilityCard(UtilityTemplate(**card)))
            case CardType.MANA:
                player_unit.add_to_field(ManaCard(ManaTemplate(**card)))
            case _:
                pass

generate_deck_from_list(give_test_card(100), player_unit=player)
generate_deck_from_list(give_test_card(100), player_unit=opponent)

player.initialize_deck()
player.shuffle_deck()
opponent.initialize_deck()
opponent.shuffle_deck()
player.draw_from_deck(7)
opponent.draw_from_deck(7)

def main():
    """
    The main() function is executed in main.py.
    """
    turn_count = 0
    while True:
        #os.system('cls' if os.name == 'nt' else 'clear')
        #TODO Buggy turn counter
        turn_count += 1
        # Lazy, but functional for now until I get a game context class
        print(f'== {cf.bold} Turn [{turn_count}] {cf.reset} ======================================================================')
        print(TerminalView.print_player_data(opponent, opposite=True))
        print(TerminalView.print_active_monster(opponent))
        print(TerminalView.print_active_monster(player, Bold=True))
        print(TerminalView.print_player_data(player))
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
        if opponent.active_monster and opponent.active_monster.health <= 0:
            print("You win!")
            os._exit(1)