import os
from core.enums import CardType, StageType
from termio.view import TerminalView


class CommandHandler:
    def __init__(self):
        pass

    def handle_ability(game_state, *args):
        pass

    @staticmethod
    def handle_activation(game_state, *args) -> bool | bool:
        """
        Handles user input for monster activation (hand -> active monster).
        
        :return: A tuple of `False` (not a turn-ending action) and `True` (action completed successfully.)
        """
        if not args:
            print("Usage: activate <card_id>")

        if game_state.player.hand[int(args[0])].card.type != CardType.MONSTER:
            print("Selected card is not a monster!")
            return (False, False)

        if game_state.player.hand[int(args[0])].card.stage != StageType.BASIC:
            print("Selected card is not a Basic monster!")
            return (False, False)

        success = game_state.player.set_active_monster(int(args[0]))
        return (False, success) # Redraw if successful, but don't end turn

    @staticmethod
    def handle_attach(game_state, *args):
        pass

    @staticmethod
    def handle_attack(game_state, *args) -> bool | bool:
        # TODO: Allow user to specify which attack to use
        success = game_state.player.active_monster.use_attack(0, game_state.player, game_state.opponent)
        if success:
            print(f"{game_state.player.title}'s turn has ended.")
        # Return the success status to determine if the turn ends
        return (success, True) # End turn and redraw if successful

    @staticmethod
    def handle_bench(game_state, *args) -> bool | bool:
        hand_string = TerminalView.get_hand_list_string(game_state.player)
        print(hand_string)
        index = input("Select card to bench by displayed ID. ")
        try:
            success = game_state.player.add_to_bench(int(index))
            return (False, success) # Redraw if successful, but don't end turn
        except KeyError:
            print(f"Invalid index: {index}")
            return (False, False)
        except ValueError:
            print(f"Invalid index: {index}")
            return (False, False)

    @staticmethod
    def handle_evolve(game_state, *args):
        pass

    @staticmethod
    def handle_exit(game_state, *args):
        print("Exiting 'cards' program.")
        os._exit(1)

    @staticmethod
    def handle_mana(game_state, *args) -> bool | bool:
        if not args:
            print("Usage: mana <type> [quantity]")
            return (False, False)

        mana_type = args[0]
        qty = 1
        if len(args) > 1:
            try:
                qty = int(args[1])
            except ValueError:
                print(f"Invalid quantity: {args[1]}")
                return (False, False)

        success = game_state.player.add_mana(game_state.player.active_monster, mana_type, qty)
        return (False, success) # Redraw if successful, but don't end turn

    @staticmethod
    def handle_show(game_state, *args) -> bool | bool:
        if args and args[0] == "hand":
            hand_string = TerminalView.get_hand_list_string(game_state.player)
            print(hand_string)
        else:
            print("Usage: show hand")
        return (False, False)

    @staticmethod
    def handle_retreat(game_state, *args):
        pass

    @staticmethod
    def handle_utility(game_state, *args):
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
