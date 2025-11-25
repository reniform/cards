import logging
from effects.effect_registry import EffectRegistry

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
        damage_val = kwargs.get("damage")
        if damage_val is None or damage_val == '':
            self.damage = 0
        elif isinstance(damage_val, str):
            # Strip non-digit characters to handle values like '30+', '20x'
            digits = "".join(filter(str.isdigit, damage_val))
            self.damage = int(digits) if digits else 0
        else:
            self.damage = int(damage_val)
        self.cost = kwargs["cost"]  # dict: ManaType: int
        self.description = kwargs["description"]
        # Convert raw effect dictionaries into executable Effect objects
        self.effects = [
            EffectRegistry.create_effect(effect_data)
            for effect_data in (kwargs.get("effects") or [])
            if EffectRegistry.create_effect(effect_data) is not None
        ]

    def execute(
        self, game_state, attacker, target, controller
    ) -> None:
        """
        Executes the attack from player to player; performs the check for mana.
        Currently only supports active monster attacks on active monsters (no bench support).

        Args:
            game_state (GameState): The current state of the game.
            attacker (PlayerUnit): The player with the monster performing the attack.
            target (PlayerUnit): The player with the monster receiving the attack.
            controller (GameController): The game controller for handling user input.
        """

        # 1. Deal base damage
        data_str = ""
        final_damage = self.damage
        # Check for weakness: multiply by the weakness value.
        if (
            target.active_monster.card.weak_type
            == attacker.active_monster.card.mana_type
        ):
            final_damage *= target.active_monster.card.weak_mult
            logger.info(f"Applying weakness on attack against {target.active_monster}.")
            data_str = f"(x{target.active_monster.card.weak_mult})"

        # Check for resistance: subtract by the resistance value
        if (
            target.active_monster.card.resist_type
            == attacker.active_monster.card.mana_type
        ):
            final_damage -= target.active_monster.card.resist_val
            logger.info(
                f"Applying resistance on attack against {target.active_monster}."
            )

        # If damage is 0 or less, it's not successful in that regard.
        damage_was_dealt = False
        if final_damage > 0:
            damage_was_dealt = target.active_monster.take_damage(final_damage)

        logger.info(f"{self.title} dealt {final_damage} damage! {data_str}")

        # 2. Execute effects
        if self.effects:
            for effect in self.effects:
                effect.execute(
                    game_state=game_state,
                    source_player=attacker,
                    target_player=target,
                    attack_dealt_damage=damage_was_dealt,
                    controller=controller,
                )

        # 3. Mark attacker flag
        attacker.active_monster.has_attacked = True
