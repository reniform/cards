import logging
from typing import TYPE_CHECKING, Dict, Any, Callable, TypedDict

from core.coins import coin

if TYPE_CHECKING:
    from models.player import PlayerUnit
    from core.game import GameState
    from controller.game_controller import GameController

logger = logging.getLogger(__name__)


class ConditionContext(TypedDict):
    """
    A structured dictionary holding all relevant state for a condition check.
    Using TypedDict provides static analysis benefits over Dict[str, Any].
    """
    game_state: "GameState"
    source_player: "PlayerUnit"
    target_player: "PlayerUnit"
    damage_was_dealt: bool
    controller: "GameController"

# A type alias for a checker function.
ConditionChecker = Callable[[ConditionContext], bool]


def check_always(context: ConditionContext) -> bool:
    """This condition is always met."""
    return True


def check_if_attack_was_successful(context: ConditionContext) -> bool:
    """Condition is met if the attack dealt damage."""
    # I have learned that the TypedDict lets us access the key directly.
    return context["damage_was_dealt"]


def check_on_coin_flip_heads(context: ConditionContext) -> bool:
    """Condition is met if a coin flip results in heads."""
    result = coin()
    logger.info(f"Coin flip for effect condition: {'HEADS' if result else 'TAILS'}.")
    return result


def check_on_coin_flip_tails(context: ConditionContext) -> bool:
    """Condition is met if a coin flip results in tails."""
    result = coin()
    logger.info(f"Coin flip for effect condition: {'HEADS' if result else 'TAILS'}.")
    return not result


def check_if_target_is_poisoned(context: ConditionContext) -> bool:
    """Condition is met if the target monster is poisoned."""
    target_monster = context["target_player"].active_monster
    if not target_monster:
        return False
    return "POISONED" in target_monster.special_conditions


# The dispatcher dictionary that maps condition names (from the database)
# to their corresponding checker functions.
CONDITION_DISPATCHER: Dict[str, ConditionChecker] = {
    "ALWAYS": check_always,
    "ONLY_IF_ATTACK_SUCCESSFUL": check_if_attack_was_successful,
    "ON_COIN_FLIP_HEADS": check_on_coin_flip_heads,
    "ON_COIN_FLIP_TAILS": check_on_coin_flip_tails,
    "IF_TARGET_POISONED": check_if_target_is_poisoned,
    # You can easily add new conditions here without changing the Attack class.
    # e.g., "IF_TARGET_ASLEEP": check_if_target_is_asleep,
}