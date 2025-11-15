import os
from termio.view import TerminalView

class CommandHandler:
    def __init__(self):
        pass

    @staticmethod
    def handle_attack(player, opponent, *args):
        # TODO: Allow user to specify which attack to use
        player.active_monster.use_attack(0, player, opponent)
    
    @staticmethod
    def handle_mana(player, opponent, *args):
        if not args:
            print("Usage: mana <type> [quantity]")
            return
        
        mana_type = args[0]
        qty = 1
        if len(args) > 1:
            try:
                qty = int(args[1])
            except ValueError:
                print(f"Invalid quantity: {args[1]}")
                return
        
        player.add_mana(mana_type, qty)
    
    @staticmethod
    def handle_exit(player, opponent, *args):
        print("Exiting 'cards' program.")
        os._exit(1)

    @staticmethod
    def handle_show(player, opponent, *args):
        if args and args[0] == 'hand':
            TerminalView.get_hand_list_string(player)
        else:
            print("Usage: show hand")

    COMMANDS = {
        'attack': handle_attack,
        'mana': handle_mana,
        'exit': handle_exit,
        'show': handle_show,
    }