import os
from core.enums import CardType
from core.carddata import give_test_card
from core.rules import RulesEngine
from termio.view import TerminalView
import logging
logger = logging.getLogger(__name__)

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

        try:
            card_id = int(args[0])
        except ValueError:
            print(f"Invalid card ID: {args[0]}")
            return (False, False)

        # 1. Validate the action with the RulesEngine.
        is_legal, reason = RulesEngine._validate_activate_action(
            game_state, game_state.active_player, card_id
        )
        if not is_legal:
            logger.warning(
                f"ACTIVATE failed for {game_state.active_player.title}: {reason}"
            )
            return (False, False)

        # 2. Execute the action.
        success = game_state.active_player.set_active_monster(card_id)
        return (False, success)  # Redraw if successful, but don't end turn

    @staticmethod
    def handle_attach(game_state, *args):
        """
        Handles the 'attach' command to attach a mana card from hand to a monster.
        Usage: attach <mana_card_id> [to <target_monster_id>]
        If no target is specified, it defaults to the active monster.
        """
        # 1. Parse arguments.
        if not args:
            print("Usage: attach <mana_card_id> [to <target_monster_id>]")
            return (False, False)

        try:
            mana_card_id = int(args[0])
            target_monster_id = None

            if len(args) >= 3 and args[1].lower() == "to":
                target_monster_id = int(args[2])
            elif game_state.active_player.active_monster:
                target_monster_id = game_state.active_player.active_monster.id

        except (ValueError, IndexError):
            print("Invalid command format. Usage: attach <mana_card_id> [to <target_monster_id>]")
            return (False, False)

        # 2. Validate the action with the RulesEngine.
        is_legal, reason = RulesEngine._validate_attach_action(
            game_state, game_state.active_player, mana_card_id, target_monster_id
        )
        if not is_legal:
            logger.warning(
                f"ATTACH failed for {game_state.active_player.title}: {reason}"
            )
            return (False, False)

        # 3. Execute the action.
        success = game_state.active_player.attach_mana(mana_card_id, target_monster_id)
        return (False, success)  # Redraw on success, but don't end turn

    @staticmethod
    def handle_attack(game_state, *args) -> bool | bool:
        """
        Handles the 'attack' command.
        Usage: attack [attack_index] [on <target_id>]
        Defaults to attack_index 0 and the opponent's active monster if not specified.
        """
        # 1. Parse arguments and set defaults.
        attack_index = 0
        target_id = None

        try:
            if args:
                attack_index = int(args[0])
            
            # Default target is the opponent's active monster.
            if game_state.waiting_player.active_monster:
                target_id = game_state.waiting_player.active_monster.id

            # Check for explicit target.
            if len(args) >= 3 and args[1].lower() == 'on':
                target_id = int(args[2])

        except (ValueError, IndexError):
            logger.warning("Invalid command format. Usage: attack [attack_index] [on <target_id>]")
            return (False, False)

        # 2. Validate the action with the RulesEngine.
        is_legal, reason = RulesEngine._validate_attack_action(game_state, game_state.active_player, attack_index, target_id)
        if not is_legal:
            logger.warning(f"ATTACK failed {game_state.active_player.title}: {reason}") # Print the specific reason for failure.
            return (False, False)

        # 3. Execute the attack.
        success = game_state.active_player.active_monster.use_attack(
            attack_index, game_state.active_player, game_state.waiting_player
        )
        if success:
            print(f"{game_state.active_player.title}'s turn has ended.")
        # Return the success status to determine if the turn ends
        return (success, True)  # End turn and redraw if successful

    @staticmethod
    def handle_bench(game_state, *args) -> bool | bool:
        """
        Handles the 'bench' command to move a monster from hand to bench.
        Usage: bench <card_id_from_hand>
        """
        if not args:
            print("Usage: bench <card_id_from_hand>")
            return (False, False)

        try:
            card_id = int(args[0])
        except ValueError:
            print(f"Invalid card ID: {args[0]}")
            return (False, False)

        # 1. Validate the action with the RulesEngine.
        is_legal, reason = RulesEngine._validate_bench_action(
            game_state, game_state.active_player, card_id
        )
        if not is_legal:
            logger.warning(
                f"BENCH failed for {game_state.active_player.title}: {reason}"
            )
            return (False, False)

        # 2. Execute the action.
        success = game_state.active_player.add_to_bench(card_id)
        return (False, success)  # Redraw if successful, but don't end turn

    @staticmethod
    def handle_evolve(game_state, *args):
        """
        Handles the 'evolve' command.
        Usage: evolve <base_monster_id> to <evolution_card_id>
        """
        # 1. Validate command structure.
        if len(args) != 3 or args[1].lower() != "to":
            print("Usage: evolve <base_monster_id> to <evolution_card_id>")
            return (False, False)

        # 2. Parse IDs.
        try:
            base_monster_id = int(args[0])
            evo_card_id = int(args[2])
        except ValueError:
            print("Invalid ID. Please provide numbers for card IDs.")
            return (False, False)

        # 3. Validate the action with the RulesEngine.
        is_legal, reason = RulesEngine._validate_evolve_action(
            game_state, game_state.active_player, evo_card_id, base_monster_id
        )
        if not is_legal:
            logger.warning(
                f"EVOLVE failed for {game_state.active_player.title}: {reason}"
            )
            return (False, False)

        # 4. Execute the action.
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
        """
        Handles the 'retreat' command.
        The player must select a benched monster to promote.
        """
        player = game_state.active_player

        # 1. Perform initial checks for retreat possibility.
        if not player.active_monster:
            print("You have no active monster to retreat.")
            return (False, False)

        if not player.bench:
            print("You have no benched monsters to promote.")
            return (False, False)

        # 2. Prompt user to select a new active monster from the bench.
        print("Your Bench:")
        print(TerminalView.print_bench(player))
        new_active_id_str = input(
            "Select a monster from your bench to promote to the active spot (by ID): "
        )

        try:
            new_active_id = int(new_active_id_str)
            # 3. Execute the retreat action.
            success = player.retreat_active_monster(new_active_id)
            return (False, success)  # Redraw on success, but don't end turn
        except (ValueError, KeyError):
            print(f"Invalid ID: '{new_active_id_str}'. Please enter a valid number.")
            return (False, False)

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
