import logging

from typing import TYPE_CHECKING
from core.enums import CardType, StageType, ManaType
from controller.commands.base_command import Command

if TYPE_CHECKING:
    from core.game import GameState

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Handles all action validation according to the game's rules.
    * **Validation methods** consider the game state and either return `True`, or `False` with an error message.
    * **Get-action methods** return a list of all possible actions of a certain type and their potential targets.
    """

    @staticmethod
    def get_illegality_reason(game_state: "GameState", command: Command) -> str:
        """
        Determines why a given command object is illegal.

        This method is called *after* a command has failed the legality check.
        It re-validates the action to produce a user-friendly reason for
        the failure.

        Args:
            game_state: The current state of the game.
            command: The illegal command object that was parsed.

        Returns:
            A string explaining why the command is illegal.
        """
        player = game_state.current_player
        command_type = command.__class__.__name__.replace("Command", "").upper()

        # Dynamically find the private validation method corresponding to the command.
        # e.g., for "ActivateCommand", it looks for "_validate_activate_action".
        validator_method_name = f"_validate_{command_type.lower()}_action"
        validator = getattr(RulesEngine, validator_method_name, None)

        if not validator:
            return f"Unknown action type '{command_type}'."

        # Call the specific validator with the command's attributes.
        # The validator returns (is_legal, reason). We only care about the reason.
        _, reason = validator(game_state, player, **command.__dict__)

        return reason or "An unknown rule prevented this action."

    @staticmethod
    def get_legal_actions(game_state, player) -> list:
        """
        Constructs a list of all permissible actions allowed to be taken by a player
        throughout the course of their turn. This list is assembled from the get-action
        methods, who perform validation checks on actions to be performed by the player
        and return a list of legal actions with plausible targets.
        """
        legal_actions = []

        # The player can pass at any time.
        legal_actions.append({"type": "PASS"})
        logger.debug(f"Legal action approved: PASS for {player.title}")

        attack_actions = RulesEngine._get_attack_actions(game_state, player)
        legal_actions.extend(attack_actions)

        activate_actions = RulesEngine._get_activate_actions(game_state, player)
        legal_actions.extend(activate_actions)

        attach_actions = RulesEngine._get_attach_actions(game_state, player)
        legal_actions.extend(attach_actions)

        bench_actions = RulesEngine._get_bench_actions(game_state, player)
        legal_actions.extend(bench_actions)

        evolve_actions = RulesEngine._get_evolve_actions(game_state, player)
        legal_actions.extend(evolve_actions)

        retreat_actions = RulesEngine._get_retreat_actions(game_state, player)
        legal_actions.extend(retreat_actions)

        use_actions = RulesEngine._get_use_actions(game_state, player)
        legal_actions.extend(use_actions)

        return legal_actions

    @staticmethod
    def _get_ability_actions(game_state, player) -> list:
        pass

    @staticmethod
    def _validate_activate_action(
        game_state, player, card_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific ACTIVATE action is legal. If not, a reason is provided.
        """
        # Check if there is already an active monster.
        if player.active_monster:
            return (False, f"{player.title} already has an active monster.")

        # Check if the card exists in the player's hand.
        card_to_activate = player.hand.get(card_id)
        if not card_to_activate:
            return (False, f"Card with ID {card_id} not found in your hand.")

        # Check if the card is a monster.
        if card_to_activate.card.type != CardType.MONSTER:
            return (
                False,
                f"Cannot activate '{card_to_activate.title}': it is not a monster.",
            )

        # Check if the monster is a Basic monster.
        if card_to_activate.card.stage != StageType.BASIC:
            return (
                False,
                f"Cannot activate '{card_to_activate.title}': it is not a Basic monster.",
            )

        # All checks pass! The action is legal.
        return (True, None)

    @staticmethod
    def _get_activate_actions(game_state, player) -> list:
        """
        Generates a list of legal ACTIVATE actions.
        """
        actions = []

        # For each card in hand, ask whether it can be validly activated.
        for card in player.hand.values():
            is_legal, _ = RulesEngine._validate_activate_action(
                game_state, player, card.id
            )
            if is_legal:
                actions.append(
                    {
                        "type": "ACTIVATE",
                        "payload": {"card_id": card.id, "card_title": card.title},
                    }
                )
                logger.debug(
                    f"Legal action approved: ACTIVATE for {card.title} ({card.id})"
                )
        return actions

    @staticmethod
    def _validate_attach_action(
        game_state, player, mana_card_id: int, target_monster_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific ATTACH action is legal. If not, a reason is provided.
        """
        # Validate the mana card.
        mana_card = player.hand.get(mana_card_id)
        if not mana_card:
            return (False, f"Card with ID {mana_card_id} not found in your hand.")
        if mana_card.card.type != CardType.MANA:
            return (False, f"Card '{mana_card.title}' is not a mana card.")

        # Validate the target monster.
        target_monster = None
        if player.active_monster and player.active_monster.id == target_monster_id:
            target_monster = player.active_monster
        else:
            target_monster = player.bench.get(target_monster_id)

        if not target_monster:
            return (
                False,
                f"Target monster with ID {target_monster_id} not found on your field.",
            )

        # Check whether the monster has already received a mana card that turn.
        if target_monster.has_attached:
            return (
                False,
                f"'{target_monster.title}' has already had mana attached this turn.",
            )

        # All checks pass! The action is legal.
        return (True, None)

    @staticmethod
    def _get_attach_actions(game_state, player) -> list:
        """
        Generates a list of legal ATTACH actions.
        """
        actions = []
        # Identify all potential mana cards to attach.
        mana_in_hand = [
            card for card in player.hand.values() if card.card.type == CardType.MANA
        ]

        # Identify all potential monster targets on the field.
        monsters_on_field = (
            [player.active_monster] if player.active_monster else []
        ) + list(player.bench.values())

        # 3. For every combination, ask whether the mana attachment is plausible.
        for mana_card in mana_in_hand:
            for target_monster in monsters_on_field:
                is_legal, _ = RulesEngine._validate_attach_action(
                    game_state, player, mana_card.id, target_monster.id
                )
                if is_legal:
                    actions.append(
                        {
                            "type": "ATTACH",
                            "payload": {
                                "mana_card_id": mana_card.id,
                                "target_monster_id": target_monster.id,
                            },
                        }
                    )
        return actions

    @staticmethod
    def _validate_attack_action(
        game_state, player, attack_index: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific ATTACK action is legal. If not, a reason is provided.
        """
        attacker = player.active_monster
        # Check for the active monster.
        if not attacker:
            return (False, f"{player.title} has no active monster to attack with.")

        # Check if the active monster has attacked already (sanity check).
        if attacker.has_attacked:
            return (
                False,
                f"{player.title}'s active monster has already attacked this turn.",
            )

        # Check for attacks on the first turn.
        if game_state.turn_count <= 1:
            return (False, f"{player.title} cannot attack on their first turn.")

        # Check for special conditions that prevent attacking.
        if "ASLEEP" in attacker.special_conditions:
            return (
                False,
                f"{player.title}'s active monster is Asleep and cannot attack.",
            )
        if "PARALYZED" in attacker.special_conditions:
            return (
                False,
                f"{player.title}'s active monster is Paralyzed and cannot attack.",
            )

        # Check for a valid attack index.
        if not (0 <= attack_index < len(attacker.card.attacks)):
            return (False, f"Invalid attack index for {attacker.title}: {attack_index}")

        # Validate the target monster.
        target_monster = game_state.waiting_player.active_monster

        if not target_monster:
            return (
                False,
                "Opponent has no active monster to attack.",
            )

        # Check for sufficient mana for the chosen attack.
        attack = attacker.card.attacks[attack_index]
        if not attacker.has_mana(attack.cost):
            return (False, f"Not enough mana for {attack.title}")

        # All checks pass! The action is legal.
        return (True, None)

    @staticmethod
    def _get_attack_actions(game_state, player) -> list:
        actions = []
        attacker = player.active_monster
        if not attacker:
            return actions

        # The only valid target is the opponent's active monster.
        target_monster = game_state.waiting_player.active_monster
        if not target_monster:
            return actions  # No targets, so no attack actions.

        # Iterate through each attack of the active monster.
        for i, attack in enumerate(attacker.card.attacks):
            is_legal, _ = RulesEngine._validate_attack_action(game_state, player, i)
            if is_legal:
                actions.append(
                    {
                        "type": "ATTACK",
                        "payload": {
                            "attack_name": attack.title,
                            "attack_index": i,
                        },
                    }
                )
                logger.debug(
                    f"Legal action approved: ATTACK '{attack.title}' (index {i}) on target {target_monster.title} (ID: {target_monster.id}) for {player.title}"
                )
        return actions

    @staticmethod
    def _validate_bench_action(
        game_state, player, card_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific BENCH action is legal. If not, a reason is provided.
        """
        card_to_bench = player.hand.get(card_id)
        # 1. Validate the monster card.
        if not card_to_bench:
            return (False, f"Card with ID {card_id} not found in your hand.")
        if card_to_bench.card.type != CardType.MONSTER:
            return (False, f"Card '{card_to_bench.title}' is not a monster card.")

        # 2. Check if the monster is Basic.
        if card_to_bench.card.stage != StageType.BASIC:
            return (False, f"Card '{card_to_bench.title}' is not a Basic monster.")

        # 3. Check if an active monster exists.
        # A player should activate a monster before benching.
        # (This should eventually be turned off for the setup stage.)
        if not player.active_monster:
            return (
                False,
                f"Player must activate a monster before benching {card_to_bench.title}.",
            )

        # 4. Check if bench is already full.
        if len(player.bench) >= player.CONST_MAX_BENCH_CARDS:
            return (
                False,
                f"Player {player.title} bench is already full (max: {player.CONST_MAX_BENCH_CARDS}.)",
            )

        # All checks pass! The action is legal.
        return (True, None)

    @staticmethod
    def _get_bench_actions(game_state, player) -> list:
        """
        Generates a list of legal BENCH actions.
        """
        actions = []
        # For each card in hand, ask the "judge" if it's a legal bench action.
        for card in player.hand.values():
            is_legal, _ = RulesEngine._validate_bench_action(
                game_state, player, card.id
            )
            if is_legal:
                actions.append(
                    {
                        "type": "BENCH",
                        "payload": {"card_id": card.id, "card_title": card.title},
                    }
                )
                logger.debug(
                    f"Legal action approved: BENCH for {card.title} ({card.id})"
                )
        return actions

    @staticmethod
    def _validate_evolve_action(
        game_state, player, evo_card_id: int, base_card_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific EVOLVE action is legal. If not, a reason is provided.
        """
        # 1. Validate the evolution card from hand.
        evo_card = player.hand.get(evo_card_id)
        if not evo_card:
            return (
                False,
                f"Evolution card with ID {evo_card_id} not found in your hand.",
            )
        if evo_card.card.type != CardType.MONSTER or evo_card.card.stage not in [
            StageType.STAGEONE,
            StageType.STAGETWO,
        ]:
            return (False, f"Card '{evo_card.title}' is not a valid evolution card.")

        # 2. Validate the base monster on the field.
        base_monster = None
        if player.active_monster and player.active_monster.id == base_card_id:
            base_monster = player.active_monster
        else:
            base_monster = player.bench.get(base_card_id)

        if not base_monster:
            return (
                False,
                f"Base monster with ID {base_card_id} not found on your field.",
            )

        # 3. Check if the evolution is a valid match.
        if evo_card.card.evolve_from != base_monster.title:
            return (
                False,
                f"'{evo_card.title}' cannot evolve from '{base_monster.title}'.",
            )

        # 4. Check the "cannot evolve on the first turn it was played" rule.
        # This requires a 'turn_played' attribute on MonsterCard, which we can add later.
        # For now, we'll skip this check.

        # 5. Check if the monster has already evolved this turn.
        if base_monster.has_evolved:
            return (False, f"'{base_monster.title}' has already evolved this turn.")

        return (True, None)

    @staticmethod
    def _get_evolve_actions(game_state, player) -> list:
        """
        Generates a list of legal EVOLVE actions.
        An EVOLVE action is possible if a player has a monster in their hand
        that can evolve from a monster they have on their field.
        """
        actions = []

        # Find all potential evolution cards in hand (Stage 1 or 2).
        evo_cards_in_hand = [
            card
            for card in player.hand.values()
            if card.card.type == CardType.MONSTER
            and card.card.stage in [StageType.STAGEONE, StageType.STAGETWO]
        ]

        # Find all potential base monsters on the field.
        monsters_on_field = (
            [player.active_monster] if player.active_monster else []
        ) + list(player.bench.values())

        # For each combination, check if the evolution is valid.
        for evo_card in evo_cards_in_hand:
            for base_monster in monsters_on_field:
                is_legal, _ = RulesEngine._validate_evolve_action( # This call was already correct
                    game_state, player, evo_card.id, base_monster.id
                )
                if is_legal:
                    actions.append(
                        {
                            "type": "EVOLVE",
                            "payload": {
                                "evo_card_id": evo_card.id,
                                "base_card_id": base_monster.id,
                            },
                        }
                    )
        return actions

    @staticmethod
    def _validate_retreat_action(
        game_state, player, new_active_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific RETREAT action is legal. If not, a reason is provided.
        """
        # 1. Check for an active monster.
        if not player.active_monster:
            return (False, "You have no active monster to retreat.")

        # 2. Check if the bench is full.
        if len(player.bench) >= player.CONST_MAX_BENCH_CARDS:
            return (False, "Your bench is full, you cannot retreat.")

        # 3. Check if the monster to promote exists on the bench.
        monster_to_promote = player.bench.get(new_active_id)
        if not monster_to_promote:
            return (False, f"Monster with ID {new_active_id} not found on your bench.")

        # 4. Check if the active monster can pay the retreat cost.
        retreat_cost = player.active_monster.card.retreat_val
        if not player.active_monster.has_mana({ManaType.COLORLESS: retreat_cost}):
            return (
                False,
                f"Not enough mana to pay retreat cost for '{player.active_monster.title}'.",
            )

        # 5. Check for special conditions that prevent retreating.
        if "ASLEEP" in player.active_monster.special_conditions:
            return (
                False,
                f"{player.title}'s active monster is Asleep and cannot retreat.",
            )
        if "PARALYZED" in player.active_monster.special_conditions:
            return (
                False,
                f"{player.title}'s active monster is Paralyzed and cannot retreat.",
            )

        # All checks pass! The action is legal.
        return (True, None)

    @staticmethod
    def _get_retreat_actions(game_state, player) -> list:
        """
        Generates a list of legal RETREAT actions.
        """
        actions = []
        # For each monster on the bench, check if it can be promoted.
        for benched_monster in player.bench.values():
            is_legal, _ = RulesEngine._validate_retreat_action(
                game_state, player, benched_monster.id
            )
            if is_legal:
                actions.append(
                    {
                        "type": "RETREAT",
                        "payload": {
                            "promoted_monster_id": benched_monster.id,
                        },
                    }
                )
        return actions

    @staticmethod
    def _validate_use_action(
        game_state, player, card_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific USE action is legal. If not, a reason is provided.
        """
        # 1. Validate the card exists in hand.
        card_to_use = player.hand.get(card_id)
        if not card_to_use:
            return (False, f"Card with ID {card_id} not found in your hand.")

        # 2. Validate the card is a utility card.
        if card_to_use.card.type != CardType.UTILITY:
            return (False, f"Card '{card_to_use.title}' is not a utility card.")

        # All checks pass! The action is legal.
        return (True, None)

    @staticmethod
    def _get_use_actions(game_state, player) -> list:
        """
        Generates a list of legal USE actions for utility cards in hand.
        """
        actions = []
        # For each card in hand, ask the "judge" if it's a legal use action.
        for card in player.hand.values():
            is_legal, _ = RulesEngine._validate_use_action(game_state, player, card.id)
            if is_legal:
                actions.append(
                    {
                        "type": "USE",
                        "payload": {"card_id": card.id, "card_title": card.title},
                    }
                )
        return actions
