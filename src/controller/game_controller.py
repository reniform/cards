import logging

from core.rules import RulesEngine
from controller.command_parser import CommandParser
from controller.commands.inspect_command import InspectCommand
from controller.commands.mana_command import ManaCommand
from controller.commands.base_command import Command

logger = logging.getLogger(__name__)


class GameController:
    def __init__(self, game_state, view):
        self.game_state = game_state
        self.view = view
        self.command_parser = CommandParser()

    def get_attack_choice(self, attacks: list) -> int:
        """
        Uses the view to prompt the current player to choose an attack from a list.

        Args:
            attacks: A list of Attack objects to choose from.

        Returns:
            The 0-based index of the chosen attack.
        """
        # This method acts as a bridge, so effects don't need to know about the view.
        return self.view.prompt_for_attack_choice(attacks)

    def _is_command_legal(self, command: Command) -> bool:
        """
        Checks if a parsed command object corresponds to a legal action.

        This method compares the parsed command against the list of pre-calculated legal 
        actions from the RulesEngine.
        """
        command_type = command.__class__.__name__.replace("Command", "").upper()

        for legal_action in self.game_state.legal_actions:
            if legal_action["type"] == command_type:
                # Get the payload from the legal action, defaulting to an empty dict.
                legal_payload = legal_action.get("payload", {})

                # Check if the command object's attributes are a superset of the
                # legal action's payload. This works for both empty and non-empty payloads.
                is_match = all(
                    # For each attribute on the command object...
                    # ...check if its value matches the value in the legal payload.
                    legal_payload.get(key) == value
                    for key, value in command.__dict__.items()
                )
                if is_match:
                    return True
        return False

    def run(self) -> None:
        """
        The main game loop.
        """
        while not self.game_state.winner:
            self.game_state.legal_actions = self.game_state.get_legal_actions(
                self.game_state.current_player
            )

            self.view.redraw_screen(self.game_state)
            command_string: str = self.view.get_command(self.game_state)

            # Handle system-level commands before parsing.
            if command_string.strip().lower() == "exit":
                logger.info("Exiting Blackstar...")
                break

            command_obj = self.command_parser.parse(command_string)

            if not command_obj:
                continue

            # Handle meta/debug commands that don't need a legality check.
            if isinstance(command_obj, (InspectCommand, ManaCommand)):
                _, needs_redraw = command_obj.execute(self.game_state)
                if needs_redraw:
                    # Loop again to redraw the screen after the meta command.
                    continue
            elif self._is_command_legal(command_obj):
                turn_ended, _ = command_obj.execute(self.game_state, self)
                if turn_ended:
                    self.game_state.next_turn()
            else:
                # If the command is illegal, ask the RulesEngine for the specific reason.
                reason = RulesEngine.get_illegality_reason(self.game_state, command_obj)
                logger.warning(f"Illegal command '{command_string}': {reason}")

            self.game_state.check_knockouts()