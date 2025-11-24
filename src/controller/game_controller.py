import logging
from controller.command_handler import CommandHandler

logger = logging.getLogger(__name__)

class GameController:
    def __init__(self, game_state, view):
        self.game_state = game_state
        self.view = view
        self.command_handler = CommandHandler()

    def run(self) -> None:
        """
        The main game loop.
        """
        while not self.game_state.winner:
            # 1. Calculate all legal actions for the current state.
            self.game_state.legal_actions = self.game_state.get_legal_actions(
                self.game_state.active_player
            )
            self.game_state.legal_action_types = {
                action["type"] for action in self.game_state.legal_actions
            }

            # 2. Redraw the screen with the new state.
            self.view.redraw_screen(self.game_state)
            command = self.view.get_command(self.game_state)

            parts = command.split()
            if not parts:
                continue

            command_word = parts[0].lower()
            args = parts[1:]

            if command_word == "debug":  # Special case to break the loop
                break
            elif handler := self.command_handler.COMMANDS.get(command_word):
                # Pass the game_state to the handler, not the controller itself.
                turn_ended, needs_redraw = handler(self.game_state, *args)
                if turn_ended:
                    self.game_state.next_turn()

            else:
                logger.warning(f"Unknown command: {command_word}")

            # 4. After any action, check for knockouts.
            self.game_state.check_knockouts()

        # After the loop breaks, announce the winner.
        logger.info(f"Game over! The winner is {self.game_state.winner.title}!")
