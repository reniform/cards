import logging
from effects.effects import EffectRegistry

logger = logging.getLogger(__name__)


class Attack:
    """
    Defines any action taken by a live monster that induces damage. Holds the following values:
    ### Basic metadata
    * `name`: The name of the attack.
    * `damage`: The hit points to be removed as a result of the damage.
    * `cost`: The cost of the attack in mana, i.e. a dict of {ManaType: amount}.
    * `effects`: A list of effects of type `Effect`.
    """

    def __init__(self, **kwargs) -> None:
        self.title = kwargs["title"]  # str
        self.damage = int(kwargs["damage"])  # int
        self.cost = kwargs["cost"]  # dict: ManaType: int
        self.description = kwargs["description"]
        # Convert raw effect dictionaries into executable Effect objects
        self.effects = [
            EffectRegistry.create_effect(effect_data)
            for effect_data in (kwargs.get("effects") or [])
            if EffectRegistry.create_effect(effect_data) is not None
        ]

    def execute(self, game_state, attacker, target) -> None:
        """
        Executes the attack from player to player; performs the check for mana.
        Currently only supports active monster attacks on active monsters (no bench support).
        TODO: MonsterCards should be attacker and target.

        Args:
            game_state (GameState): The current state of the game.
            attacker (PlayerUnit): The player with the monster performing the attack.
            target (PlayerUnit): The player with the monster receiving the attack.
        """

        # 1. Deal base damage
        data_str = ""
        final_damage = self.damage
        # Check for weakness: multiply by the weakness value.
        if target.active_monster.card.weak_type == attacker.active_monster.card.mana_type:
            final_damage *= target.active_monster.card.weak_mult
            logger.info(f"Applying weakness on attack against {target.active_monster}.")
            data_str = f"(x{target.active_monster.card.weak_mult})"

        # Check for resistance: subtract by the resistance value
        if target.active_monster.card.resist_type == attacker.active_monster.card.mana_type:
            final_damage -= target.active_monster.card.resist_val
            logger.info(f"Applying resistance on attack against {target.active_monster}.")

        target.active_monster.take_damage(final_damage)
        logger.info(f"{self.title} dealt {final_damage} damage! {data_str}")

        # 2. Execute effects
        if self.effects:
            for effect in self.effects:
                effect.execute(
                    game_state=game_state,
                    source_player = attacker,
                    target_player = target
                )

        # 3. Mark attacker flag
        attacker.active_monster.has_attacked = True


class Effect:
    """"""
