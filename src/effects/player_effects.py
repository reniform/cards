from typing import TYPE_CHECKING
from .base_effect import Effect
from .effect_registry import EffectRegistry

if TYPE_CHECKING:
    from core.game import GameState
    from models.player import PlayerUnit


@EffectRegistry.register("draw_from_deck")
class DrawEffect(Effect):
    """
    `DrawEffect` (corresponding registration string: `draw_from_deck`)
    produces a drawn card in the player.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.amount = self.value or 1  # Use 'value' from DB

    def execute(self, **kwargs) -> None:
        target_player: "PlayerUnit" = kwargs.get("target_player")

        target_player.draw_from_deck(self.amount)
        # no return: player modified directly