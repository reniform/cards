from typing import TYPE_CHECKING
from .base_effect import Effect
from .effect_registry import EffectRegistry
from logging import getLogger

logger = getLogger(__name__)


if TYPE_CHECKING:
    from core.game import GameState
    from models.player import PlayerUnit


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

    def execute(self, game_state: 'GameState', source_player: 'PlayerUnit', target_player: 'PlayerUnit') -> None:
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
    
    def execute(self, game_state: 'GameState', source_player: 'PlayerUnit', target_player: 'PlayerUnit') -> None:
        if self.damage_amount <= 0:
            return
        
        # Delegate the condition check to the base class.
        if self.should_execute():
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

    def execute(self, game_state: 'GameState', source_player: 'PlayerUnit', target_player: 'PlayerUnit') -> None:
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

        # Resolve conditions

        # Apply the heal, but only up to its max health.
        target_monster.health = min(
            target_monster.card.health, target_monster.health + self.heal_amount
        )
        logger.info(f"Healed {target_monster.title} for {self.heal_amount} HP.")

@EffectRegistry.register("SET_IMMUNE")
class SetImmuneEffect(Effect):
    """
    `SetImmuneEffect` (corresponding registration string: `SET_IMMUNE`)
    makes a monster immune to damage and effects until the end of the next turn.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(
        self, game_state: "GameState", source_player: "PlayerUnit", target_player: "PlayerUnit"
    ) -> None:
        target_monster = None
        if self.target == "SELF":
            target_monster = source_player.active_monster
        elif self.target == "DEFENDING_MONSTER":
            target_monster = target_player.active_monster

        if target_monster:
            target_monster.is_immune = True
            logger.info(f"{target_monster.title} is now immune to damage and effects.")