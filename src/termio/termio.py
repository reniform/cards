import os
from termio.view import TerminalView


class CommandHandler:
    def __init__(self):
        pass

    def handle_ability(player, opponent, *args):
        pass

    @staticmethod
    def handle_activation(player, opponent, *args):
        pass

    @staticmethod
    def handle_attach(player, opponent, *args):
        pass

    @staticmethod
    def handle_attack(player, opponent, *args):
        # TODO: Allow user to specify which attack to use
        player.active_monster.use_attack(0, player, opponent)

    @staticmethod
    def handle_bench(player, opponent, *args):
        hand_string = TerminalView.get_hand_list_string(player)
        print(hand_string)
        index = input("Select card to bench by displayed ID. ")
        try:
            player.add_to_bench(int(index))
        except KeyError:
            print(f"Invalid index: {index}")
            return
        except ValueError:
            print(f"Invalid index: {index}")
            return

    @staticmethod
    def handle_evolve(player, opponent, *args):
        pass

    @staticmethod
    def handle_exit(player, opponent, *args):
        print("Exiting 'cards' program.")
        os._exit(1)

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

        player.add_mana(player.active_monster, mana_type, qty)

    @staticmethod
    def handle_show(player, opponent, *args):
        if args and args[0] == "hand":
            hand_string = TerminalView.get_hand_list_string(player)
            print(hand_string)
        else:
            print("Usage: show hand")

    @staticmethod
    def handle_retreat(player, opponent, *args):
        pass

    @staticmethod
    def handle_utility(player, opponent, *args):
        pass

    COMMANDS = {
        "ability": handle_ability,
        "activate": handle_activation,
        "attach": handle_attach,
        "attack": handle_attack,
        "bench": handle_bench,
        "evolve": handle_evolve,
        "exit": handle_exit,
        "mana": handle_mana,
        "show": handle_show,
        "retreat": handle_retreat,
        "utility": handle_utility,
    }
