import os
from core.enums import CardType, StageType
from core.carddata import give_test_card
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
            return (False, False)
        
        try:
            card_id = int(args[0])
            success = game_state.player.set_active_monster(card_id)
            if not success:
                print("Could not activate monster. Check logs for details.")
            return (False, success) # Redraw if successful, but don't end turn
        except (ValueError, KeyError):
            print(f"Invalid card ID: {args[0]}")
            return (False, False)

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
    def handle_reset(game_state, *args) -> bool | bool:
        """
        Resets the entire game state for testing.
        """
        print("Resetting game state...")
        
        # This logic is mirrored from main.py
        game_state.player.reset()
        game_state.opponent.reset()

        from main import generate_deck_from_list # Local import to avoid circular dependency
        generate_deck_from_list(give_test_card(100), player_unit=game_state.player)
        generate_deck_from_list(give_test_card(100), player_unit=game_state.opponent)

        # Initialize, shuffle, and draw for both players
        game_state.player.initialize_deck()
        game_state.player.shuffle_deck()
        game_state.player.draw_from_deck(7)

        game_state.opponent.initialize_deck()
        game_state.opponent.shuffle_deck()
        game_state.opponent.draw_from_deck(7)

        # Pre-activating an opponent monster (test).
        for card_id, card in game_state.opponent.hand.items():
            if card.card.type == CardType.MONSTER:
                game_state.opponent.set_active_monster(card_id)
                # This break ensures we only activate the first monster found.
                break

        print("Game has been reset.")
        return (False, True) # Redraw the screen    

    @staticmethod
    def handle_retreat(game_state, *args):
        pass

    @staticmethod
    def handle_utility(game_state, *args):
        """
        Handles the 'use' command for playing a utility card from the hand.

        :return: A tuple of `False` (not a turn-ending action) and `True` (action completed successfully.)
        """
        if not args:
            print("Usage: use <card_id_from_hand>")
            return (False, False)
        
        # Validate card ID.
        try:
            card_id_to_use = int(args[0])
        except ValueError:
            print(f"Invalid card ID: {args[0]}. Please provide a number.")
            return (False, False)

        card_in_hand = game_state.player.hand.get(card_id_to_use)

        if not card_in_hand:
            print(f"Card with ID {card_id_to_use} not found in your hand.")
            return (False, False)
        
        if card_in_hand.card.type != CardType.UTILITY:
            print(f"Card '{card_in_hand.title}' is not a utility card.")
            return (False, False)
        
        success = game_state.player.use_utility_card(card_id_to_use, game_state)
        return (False, success)


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
        "reset": handle_reset,
        "retreat": handle_retreat,
        "use": handle_utility, # alias 
    }
