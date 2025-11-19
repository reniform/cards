import os
from core.enums import CardType, StageType
from core.carddata import give_test_card
from termio.view import TerminalView


class CommandHandler:
    def handle_ability(game_state, *args):
        pass

    @staticmethod
    def handle_activation(game_state, *args) -> bool | bool:
        """
        Handles user input for monster activation (hand -> active monster).

        :return: A tuple of `False` (not a turn-ending action) and `True` (action completed successfully.)
        """
        if not args:
            print("Usage: activate <card_id_from_hand>")
            return (False, False)

        # 1. Check if activating is a legal action type right now.
        if "ACTIVATE" not in game_state.legal_action_types:
            print("You can't activate a monster right now (one is already active).")
            return (False, False)

        try:
            card_id = int(args[0])
            # 2. Check if activating THIS SPECIFIC card is a legal action.
            is_legal = any(
                action["payload"]["card_id"] == card_id
                for action in game_state.legal_actions
                if action["type"] == "ACTIVATE"
            )
            if not is_legal:
                print(
                    f"Card ID {card_id} is not a valid monster to activate from your hand."
                )
                return (False, False)

            success = game_state.active_player.set_active_monster(card_id)
            if not success:
                print("Could not activate monster. Check logs for details.")
            return (False, success)  # Redraw if successful, but don't end turn
        except (ValueError, KeyError):
            print(f"Invalid card ID: {args[0]}")
            return (False, False)

    @staticmethod
    def handle_attach(game_state, *args):
        """
        Handles the 'attach' command to attach a mana card from hand to a monster.
        Usage: attach <mana_card_id> [to <target_monster_id>]
        """
        # 1. Check if attaching is a legal action type right now.
        if "ATTACH" not in game_state.legal_action_types:
            print("You can't attach a mana card right now.")
            return (False, False)

        # 1. Validate command structure and parse IDs
        if len(args) == 1:
            # Default to active monster if only one argument is given
            if not game_state.active_player.active_monster:
                print("No active monster. Please specify a target: attach <id> to <id>")
                return (False, False)
            try:
                mana_card_id = int(args[0])
                target_monster_id = game_state.active_player.active_monster.id
            except ValueError:
                print("Invalid ID. Please provide a number for the mana card ID.")
                return (False, False)
        elif len(args) == 3 and args[1].lower() == "to":
            # Handle explicit target
            try:
                mana_card_id = int(args[0])
                target_monster_id = int(args[2])
            except ValueError:
                print("Invalid ID. Please provide numbers for card IDs.")
                return (False, False)
        else:
            print("Usage: attach <mana_card_id> [to <target_monster_id>]")
            return (False, False)

        # 2. Check if this specific attachment is a legal action.
        is_legal = any(
            action["payload"]["mana_card_id"] == mana_card_id
            and action["payload"]["target_monster_id"] == target_monster_id
            for action in game_state.legal_actions
            if action["type"] == "ATTACH"
        )
        if not is_legal:
            print(
                f"Attaching mana card {mana_card_id} to monster {target_monster_id} is not a legal move right now."
            )
            return (False, False)

        # 3. Execute the action
        success = game_state.active_player.attach_mana(mana_card_id, target_monster_id)
        return (False, success)  # Redraw on success, but don't end turn

    @staticmethod
    def handle_attack(game_state, *args) -> bool | bool:
        if "ATTACK" not in game_state.legal_action_types:
            print("You can't attack right now.")
            return (False, False)

        # TODO: Allow user to specify which attack to use
        success = game_state.active_player.active_monster.use_attack(
            0, game_state.active_player, game_state.waiting_player
        )
        if success:
            print(f"{game_state.active_player.title}'s turn has ended.")
        # Return the success status to determine if the turn ends
        return (success, True)  # End turn and redraw if successful

    @staticmethod
    def handle_bench(game_state, *args) -> bool | bool:
        hand_string = TerminalView.get_hand_list_string(game_state.active_player)
        print(hand_string)
        index = input("Select card to bench by displayed ID. ")
        try:
            success = game_state.active_player.add_to_bench(int(index))
            return (False, success)  # Redraw if successful, but don't end turn
        except KeyError:
            print(f"Invalid index: {index}")
            return (False, False)
        except ValueError:
            print(f"Invalid index: {index}")
            return (False, False)

    @staticmethod
    def handle_evolve(game_state, *args):
        """
        Handles the 'evolve' command.
        Usage: evolve <evolution_card_id> from <base_monster_id>
        """
        # 1. Check if evolving is a legal action type.
        if "EVOLVE" not in game_state.legal_action_types:
            print("You have no valid evolutions at this time.")
            return (False, False)

        # 2. Validate command structure.
        if len(args) != 3 or args[1].lower() != "from":
            print("Usage: evolve <evolution_card_id> from <base_monster_id>")
            return (False, False)

        # 3. Parse and validate IDs.
        try:
            evo_card_id = int(args[0])
            base_monster_id = int(args[2])
        except ValueError:
            print("Invalid ID. Please provide numbers for card IDs.")
            return (False, False)

        # 4. Check if this specific evolution is a legal action.
        is_legal = any(
            action["payload"]["evolution_card_id"] == evo_card_id
            and action["payload"]["base_monster_id"] == base_monster_id
            for action in game_state.legal_actions
            if action["type"] == "EVOLVE"
        )
        if not is_legal:
            print(
                f"Evolving monster {base_monster_id} with card {evo_card_id} is not a legal move."
            )
            return (False, False)

        # 5. Execute the action.
        success = game_state.active_player.evolve_monster(evo_card_id, base_monster_id)
        return (False, success)  # Redraw on success, but don't end turn

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

        success = game_state.active_player.add_mana(
            game_state.active_player.active_monster, mana_type, qty
        )
        return (False, success)  # Redraw if successful, but don't end turn

    @staticmethod
    def handle_pass(game_state, *args):
        """Ends the current player's turn."""
        return (
            True,
            False,
        )  # End the turn, no redraw needed here (main loop handles it)

    @staticmethod
    def handle_show(game_state, *args) -> bool | bool:
        if args and args[0] == "hand":
            hand_string = TerminalView.get_hand_list_string(game_state.active_player)
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
        game_state.player1.reset()
        game_state.player2.reset()

        from main import (
            generate_deck_from_list,
        )  # Local import to avoid circular dependency

        generate_deck_from_list(give_test_card(100), player_unit=game_state.player1)
        generate_deck_from_list(give_test_card(100), player_unit=game_state.player2)

        # Initialize, shuffle, and draw for both players
        game_state.player1.initialize_deck()
        game_state.player1.shuffle_deck()
        game_state.player1.draw_from_deck(7)

        game_state.player2.initialize_deck()
        game_state.player2.shuffle_deck()
        game_state.player2.draw_from_deck(7)

        # Pre-activating an opponent monster (test).
        for card_id, card in game_state.player2.hand.items():
            if card.card.type == CardType.MONSTER:
                game_state.player2.set_active_monster(card_id)
                # This break ensures we only activate the first monster found.
                break

        # Pre-activating a player monster (test).
        for card_id, card in game_state.player1.hand.items():
            if card.card.type == CardType.MONSTER:
                game_state.player1.set_active_monster(card_id)
                break

        print("Game has been reset.")
        return (False, True)  # Redraw the screen

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

        card_in_hand = game_state.active_player.hand.get(card_id_to_use)

        if not card_in_hand:
            print(f"Card with ID {card_id_to_use} not found in your hand.")
            return (False, False)

        if card_in_hand.card.type != CardType.UTILITY:
            print(f"Card '{card_in_hand.title}' is not a utility card.")
            return (False, False)

        success = game_state.active_player.use_utility_card(card_id_to_use, game_state)
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
        "pass": handle_pass,
        "show": handle_show,
        "reset": handle_reset,
        "retreat": handle_retreat,
        "use": handle_utility,  # alias
    }
