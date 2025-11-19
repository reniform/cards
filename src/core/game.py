import logging
import os

import colorful as cf

from core.rules import RulesEngine
from termio.termio import CommandHandler
from termio.view import TerminalView

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, player, opponent):
        self.player1 = player
        self.player2 = opponent
        self.turn_count = 1
        self.active_player = self.player1
        self.current_phase = "main"
        self.legal_actions = []
        self.legal_action_types = set()

    @property
    def waiting_player(self):
        """A property to easily get the player who is not active."""
        return self.player2 if self.active_player is self.player1 else self.player1

    def get_legal_actions(self, player):
        return RulesEngine.get_legal_actions(self, player)

    def next_turn(self) -> None:
        """
        Handles all end-of-turn and start-of-turn logic.
        This includes swapping the active player and drawing a card for the new player.
        """
        # Swap the active player.
        # TODO: IMPLEMENT SWITCH FOR SINGLE OR MULTI ONCE HEURISTICS MODEL IS UP
        self.active_player = self.waiting_player
        self.turn_count += 1

        # Reset monster card flags.
        if self.active_player.active_monster:
            self.active_player.active_monster.has_attacked = False
            self.active_player.active_monster.has_attached = False
        for monster in self.active_player.bench:
            monster.has_attacked = False
            monster.has_attached = False

        # The new active player draws a card.
        if len(self.active_player.deck) > 0:
            self.active_player.draw_from_deck(1)

    def redraw_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

        print(self.legal_actions)  # Keep this for debugging

        print(
            f"\n== {cf.bold} Turn [{self.turn_count}] {cf.reset} ======================================================================"
        )
        print(TerminalView.print_player_data(self.waiting_player, opposite=True))
        print(TerminalView.print_bench(self.waiting_player))
        print(TerminalView.print_active_monster(self.waiting_player))
        print(TerminalView.print_active_monster(self.active_player, Bold=True))
        print(TerminalView.print_bench(self.active_player))
        print(TerminalView.print_player_data(self.active_player))
        print(TerminalView.print_hand(self.active_player))
        print(TerminalView.print_prompt(self.legal_action_types))

    def run(self) -> None:
        """
        The main game loop.
        """
        while True:
            # 1. Calculate all legal actions for the current state.
            self.legal_actions = self.get_legal_actions(self.active_player)
            self.legal_action_types = {action["type"] for action in self.legal_actions}

            # 2. Redraw the screen with the new state.
            self.redraw_screen()
            command = input(f"[{self.active_player.title}] perform an action! ==> ")

            parts = command.split()
            if not parts:
                continue

            command_word = parts[0]
            args = parts[1:]

            if command_word == "debug":  # Special case to break the loop
                break
            elif handler := CommandHandler.COMMANDS.get(command_word):
                # Pass the whole game state to the handler
                turn_ended, needs_redraw = handler(self, *args)
                if turn_ended:
                    self.next_turn()
                # The loop will automatically redraw on the next iteration.

            else:
                print("??? What???")

            # PERFORM CHECKS
            if (
                self.waiting_player.active_monster
                and self.waiting_player.active_monster.health <= 0
            ):
                print("You win!")
                os._exit(1)
