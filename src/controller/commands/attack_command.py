from typing import TYPE_CHECKING

from .base_command import Command

if TYPE_CHECKING:
    from core.game import GameState


class AttackCommand(Command):
    """
    ATTACK allows for the active monster to perform an attack on a target.
    """

    def __init__(self, attack_index: int):
        """
        Initializes the `AttackCommand` object.

        Args:
            attack_index: The index of the attack from the monster's list.
        """
        self.attack_index = attack_index

    def execute(self, game_state: "GameState") -> tuple[bool, bool]:
        """
        Executes the ATTACK action.

        This command uses the active monster's specified attack against the
        opponent's active monster. After the attack, it checks for knockouts.
        This action ends the player's turn.

        Returns:
            A tuple `(True, True)` indicating the turn has ended and the view
            needs to be redrawn.
        """
        attacker = game_state.current_player
        defender = game_state.waiting_player

        # The use_attack method on the monster handles the core logic.
        # We pass both players to give the attack's effects full context.
        attacker.active_monster.use_attack(
            attack_index=self.attack_index,
            game_state=game_state,
            player=attacker,
            target=defender,
        )

        # After damage and effects are applied, check for knockouts.
        game_state.check_knockouts()

        # Attacking always ends the turn.
        return (True, True)
