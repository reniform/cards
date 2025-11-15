import os

class CommandHandler:
    def __init__(self):
        pass

    def handle_attack(player, opponent, *args):
        player.active_monster.use_attack(0, player, opponent)
    
    def handle_mana(player, opponent, *args):
        manaType = opponent
        qty = args[0]
        player.add_mana(manaType, qty)
    
    def handle_exit(player, opponent, *args):
        print("Exiting 'cards' program.")
        os._exit(1)

    COMMANDS = {
        'attack': handle_attack,
        'mana': handle_mana,
        'exit': handle_exit
    }