import logging
from typing import Optional

from .commands.activate_command import ActivateCommand
from .commands.attack_command import AttackCommand
from .commands.attach_command import AttachCommand
from .commands.bench_command import BenchCommand
from .commands.base_command import Command
from .commands.evolve_command import EvolveCommand
from .commands.pass_command import PassCommand
from .commands.inspect_command import InspectCommand
from .commands.mana_command import ManaCommand
from .commands.retreat_command import RetreatCommand
from .commands.use_command import UseCommand

logger = logging.getLogger(__name__)


class CommandParser:
    """
    Parses raw string input from the user and converts it into a Command object.
    """
    def __init__(self):
        """Initializes the CommandParser."""
        pass

    def parse(self, command_string: str) -> Optional[Command]:
        """
        Parses a command string and returns the corresponding Command object.

        Args:
            command_string: The raw string input from the user.

        Returns:
            A Command object if parsing is successful, otherwise `None`.
        """
        parts = command_string.strip().lower().split()
        if not parts:
            return None

        command_word = parts[0]
        args = parts[1:]

        try:
            # Zero-argument commands
            if command_word == "pass":
                return PassCommand()
            
            # One-argument commands
            elif command_word in ["activate", "bench", "use", "retreat", "inspect", "attack"]:
                if len(args) != 1:
                    logger.warning(f"'{command_word}' expects 1 argument, got {len(args)}.")
                    return None
                card_id = int(args[0])
                if command_word == "activate":
                    return ActivateCommand(card_id=card_id)
                elif command_word == "bench":
                    return BenchCommand(card_id=card_id)
                elif command_word == "use":
                    return UseCommand(card_id=card_id)
                elif command_word == "retreat":
                    return RetreatCommand(promoted_card_id=card_id)
                elif command_word == "inspect":
                    return InspectCommand(card_id=card_id)
                elif command_word == "attack":
                    return AttackCommand(attack_index=card_id)
                
            # Two-command arguments
            elif command_word in ["attach", "evolve"]:
                if len(args) != 2:
                    logger.warning(f"'{command_word}' expects 2 arguments, got {len(args)}.")
                    return None
                arg1 = int(args[0])
                arg2 = int(args[1])
                if command_word == "attach":
                    return AttachCommand(mana_card_id=arg1, target_id=arg2)
                elif command_word == "evolve":
                    return EvolveCommand(evo_card_id=arg1, base_card_id=arg2)
            
            # Three-argument commands
            elif command_word == "mana": # Can take 2 or 3 arguments
                if len(args) not in [2, 3]:
                    logger.warning(f"'mana' expects 2 or 3 arguments, got {len(args)}.")
                    return None
                
                if len(args) == 3:
                    # mana <target_id> <type> <qty>
                    target_id = int(args[0])
                    mana_type = args[1]
                    quantity = int(args[2])
                    return ManaCommand(mana_type=mana_type, quantity=quantity, target_id=target_id)
                else: # len(args) == 2
                    # mana <type> <qty> (target is defaulted to active monster)
                    mana_type = args[0]
                    quantity = int(args[1])
                    return ManaCommand(mana_type=mana_type, quantity=quantity)

            else:
                logger.warning(f"Unknown command: '{command_word}'")
                return None

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing command '{command_string}': {e}")
            return None