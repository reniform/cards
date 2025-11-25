from typing import TYPE_CHECKING
import copy
from .base_effect import Effect
from .effect_registry import EffectRegistry
from logging import getLogger

logger = getLogger(__name__)


if TYPE_CHECKING:
    from core.game import GameState
    from models.player import PlayerUnit
    from controller.game_controller import GameController


@EffectRegistry.register("APPLY_STATUS")
class ApplyStatusEffect(Effect):
    """
    `ApplyStatusEffect` (corresponding registration string: `APPLY_STATUS`)
    applies a special condition to a target monster.
    The `value` from the database should be the name of the status (e.g., "ASLEEP", "POISONED").
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_to_apply = self.value  # e.g., "POISONED", "CONFUSED"

    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: "PlayerUnit",
        attack_dealt_damage: bool | None = None,
        controller: "GameController" | None = None,
    ) -> None:
        if not self.status_to_apply:
            logger.warning("ApplyStatusEffect has no 'value' to apply.")
            return

        target_monster = None
        if self.target == "SELF":
            target_monster = source_player.active_monster
        elif self.target == "DEFENDING_MONSTER":
            target_monster = target_player.active_monster

        if target_monster:
            target_monster.add_special_condition(self.status_to_apply)
            logger.info(f"Applied '{self.status_to_apply}' to {target_monster.title}.")


@EffectRegistry.register("DAMAGE_SELF")
class DamageSelfEffect(Effect):
    """
    `DamageSelfEffect` (corresponding registration string: `DAMAGE_SELF`)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.damage_amount = int(self.value)
        except ValueError:
            logger.error(f"Invalid damage 'value' for DamageSelfEffect: {self.value}")
            self.damage_amount = 0
    
    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: "PlayerUnit",
        attack_dealt_damage: bool | None = None,
        controller: "GameController" | None = None,
    ) -> None:
        if self.damage_amount <= 0:
            return
        
        # Delegate the condition check to the base class.
        if self.should_execute(attack_dealt_damage):
            source_player.active_monster.take_damage(self.damage_amount)
            logger.info(f"Dealt {self.damage_amount} damage to {source_player.active_monster.title}.")
        else:
            logger.info(f"Condition '{self.condition}' not met. No self-damage.")


@EffectRegistry.register("HEAL")
class HealEffect(Effect):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.heal_amount = int(self.value)
        except ValueError:
            logger.error(f"Invalid heal 'value' for HealEffect: {self.value}")
            self.heal_amount = 0

    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: "PlayerUnit",
        attack_dealt_damage: bool | None = None,
        controller: "GameController" | None = None,
    ) -> None:
        if self.heal_amount <= 0:
            return

        # Resolve targets
        target_monster = None
        if self.target == "SELF":
            target_monster = source_player.active_monster
        elif self.target == "TARGET":
            target_monster = target_player.active_monster

        if not target_monster:
            logger.warning(
                f"HealEffect: Could not find a valid monster for target '{self.target}'."
            )
            return

        # Use the base class to check all conditions.
        if self.should_execute(attack_dealt_damage):
            # Apply the heal, but only up to its max health.
            target_monster.health = min(
                target_monster.card.health, target_monster.health + self.heal_amount
            )
            logger.info(f"Healed {target_monster.title} for {self.heal_amount} HP.")
        else:
            logger.info("Condition for HealEffect not met. No heal applied.")

@EffectRegistry.register("SET_IMMUNE")
class SetImmuneEffect(Effect):
    """
    `SetImmuneEffect` (corresponding registration string: `SET_IMMUNE`)
    makes a monster immune to damage and effects until the end of the next turn.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: "PlayerUnit",
        attack_dealt_damage: bool | None = None,
        controller: "GameController" | None = None,
    ) -> None:
        target_monster = None
        if self.target == "SELF":
            target_monster = source_player.active_monster
        elif self.target == "DEFENDING_MONSTER":
            target_monster = target_player.active_monster

        if target_monster:
            target_monster.is_immune = True
            logger.info(f"{target_monster.title} is now immune to damage and effects.")


@EffectRegistry.register("COPY_ATTACK")
class CopyAttackEffect(Effect):
    """
    `CopyAttackEffect` (corresponding registration string: `COPY_ATTACK`)
    Copies an attack from the defending monster and executes it.
    The `condition` from the database (e.g., "KEEP_ENERGY") determines how costs are handled.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(
        self,
        game_state: "GameState",
        source_player: "PlayerUnit",
        target_player: "PlayerUnit",
        attack_dealt_damage: bool | None = None,
        controller: "GameController" | None = None,
    ) -> None:
        if not controller:
            logger.error("CopyAttackEffect requires a controller to get player input.")
            return

        defending_monster = target_player.active_monster
        if not defending_monster or not defending_monster.card.attacks:
            logger.info(f"{defending_monster.title} has no attacks to copy.")
            return

        # 1. Get the list of attacks and prompt the player for a choice.
        attacks_to_copy = defending_monster.card.attacks
        chosen_attack_index = controller.get_attack_choice(attacks_to_copy)
        original_attack = attacks_to_copy[chosen_attack_index]

        # 2. Create a deep copy to modify without affecting the original card.
        copied_attack = copy.deepcopy(original_attack)
        logger.info(
            f"{source_player.active_monster.title} is using Metronome to copy {copied_attack.title}!"
        )

        # 3. Modify the copy to ignore costs, as per the card text.
        copied_attack.cost = {}
        # We can also filter out effects like "discard energy" here in the future.
        # For example:
        # copied_attack.effects = [eff for eff in copied_attack.effects if not isinstance(eff, DiscardEnergyEffect)]

        # 4. Execute the modified attack. The attacker is still the source player.
        copied_attack.execute(game_state, source_player, target_player, controller)