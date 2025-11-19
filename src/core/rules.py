import logging

from core.enums import CardType, StageType


logger = logging.getLogger(__name__)


class RulesEngine:
    @staticmethod
    def get_legal_actions(game_state, player) -> list:
        """
        Constructs a list of all valid actions a player can take.
        """
        legal_actions = []

        # --- Check: Can the player PASS? ---
        # (Almost always yes during their turn.)
        legal_actions.append({"type": "PASS"})
        logger.debug(f"Legal action approved: PASS for {player.title}")

        # --- Check: Can the player ATTACK? ---
        # Player who goes first cannot attack on their first turn (turn_count == 1).
        # For target discovery, see get_valid_targets() below.
        attack_actions = RulesEngine._get_attack_actions(game_state, player)
        legal_actions.extend(attack_actions)

        # --- Check: Can the player ACTIVATE a monster? ---
        activate_actions = RulesEngine._get_activate_actions(game_state, player)
        legal_actions.extend(activate_actions)

        #  --- Check: Can the player ATTACH mana?
        # The rule is one mana attachment per turn.
        attach_actions = RulesEngine._get_attach_actions(game_state, player)
        legal_actions.extend(attach_actions)

        # --- Check: Can the player BENCH a monster? ---
        bench_actions = RulesEngine._get_bench_actions(game_state, player)
        legal_actions.extend(bench_actions)

        # --- Check: Can the player EVOLVE a monster? ---
        evolve_actions = RulesEngine._get_evolve_actions(game_state, player)
        legal_actions.extend(evolve_actions)

        return legal_actions

    @staticmethod
    def _get_ability_actions(game_state, player) -> list:
        pass

    @staticmethod
    def _validate_activate_action(
        game_state, player, card_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific activate action is legal, returning a reason for failure.
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
        An ACTIVATE action is possible if the player has no active monster
        and has a Basic Monster in their hand.
        """
        actions = []

        # For each card in hand, ask the "judge" if it's a legal activation.
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
        Validates if a specific attach action is legal, returning a reason for failure.
        """
        # 1. Validate the mana card.
        mana_card = player.hand.get(mana_card_id)
        if not mana_card:
            return (False, f"Card with ID {mana_card_id} not found in your hand.")
        if mana_card.card.type != CardType.MANA:
            return (False, f"Card '{mana_card.title}' is not a mana card.")

        # 2. Validate the target monster.
        target_monster = None
        if player.active_monster and player.active_monster.id == target_monster_id:
            target_monster = player.active_monster
        else:
            target_monster = player.bench.get(target_monster_id)

        if not target_monster:
            return (False, f"Target monster with ID {target_monster_id} not found on your field.")

        # 3. Check the "one attachment per monster per turn" rule.
        if target_monster.has_attached:
            return (False, f"'{target_monster.title}' has already had mana attached this turn.")

        # All checks pass! The action is legal.
        return (True, None)
        
    @staticmethod
    def _get_attach_actions(game_state, player) -> list:
        """
        Generates a list of legal ATTACH actions.
        An ATTACH action is possible if the player has a monster to attach
        a mana card to, with one mana attachment per monster allowed.
        The player can only attach one mana card per monster per turn.
        """
        actions = []
        # 1. Identify all potential mana cards to attach.
        mana_in_hand = [
            card for card in player.hand.values() if card.card.type == CardType.MANA
        ]
 
        # 2. Identify all potential monster targets on the field.
        monsters_on_field = (
            [player.active_monster] if player.active_monster else []
        ) + list(player.bench.values())
 
        # 3. For every combination, ask the "judge" if the action is legal.
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
        game_state, player, attack_index: int, target_monster_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific attack action is legal, returning a reason for failure.

        Args:
            game_state (GameState): The current state of the game.
            player (PlayerUnit): The player attempting the action.
            attack_index (int): The index of the attack being used.
            target_monster_id (int): The ID of the monster being targeted.

        Returns:
            A tuple of (bool, str | None): (True, None) if legal, (False, "reason") if illegal.
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
        if "sleep" in attacker.special_conditions:
            return (
                False,
                f"{player.title}'s active monster is Asleep and cannot attack.",
            )
        if "paralyzed" in attacker.special_conditions:
            return (
                False,
                f"{player.title}'s active monster is Paralyzed and cannot attack.",
            )

        # Check for a valid attack index.
        if not (0 <= attack_index < len(attacker.card.attacks)):
            return (False, f"Invalid attack index for {attacker.title}: {attack_index}")

        # Validate the target monster.
        target_monster = None
        if (
            game_state.waiting_player.active_monster
            and game_state.waiting_player.active_monster.id == target_monster_id
        ):
            target_monster = game_state.waiting_player.active_monster
        # TODO: Implement bench sniping.
        # elif game_state.waiting_player.bench.get(target_monster_id):
        #     target_monster = game_state.waiting_player.bench.get(target_monster_id)

        if not target_monster:
            return (
                False,
                f"Target monster with ID {target_monster_id} not found or not a valid target.",
            )

        # Current rule: only active monster can be targeted.
        if target_monster != game_state.waiting_player.active_monster:
            return (False, "You can only attack the opponent's active monster.")

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

        # Identify potential target monsters (currently only the opponent's active monster).
        potential_target_monsters = []
        if game_state.waiting_player.active_monster:
            potential_target_monsters.append(game_state.waiting_player.active_monster)

        if not potential_target_monsters:
            return actions  # No targets, so no attack actions.

        # Iterate through each attack of the active monster.
        for i, attack in enumerate(attacker.card.attacks):
            # For each attack, check against all potential targets.
            for target_monster in potential_target_monsters:
                is_legal, _ = RulesEngine._validate_attack_action(
                    game_state, player, i, target_monster.id
                )
                if is_legal:
                    actions.append(
                        {
                            "type": "ATTACK",
                            "payload": {
                                "attack_name": attack.title,
                                "attack_index": i,
                                "target_id": target_monster.id,
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
        Validates if a specific bench option is legal, returning a reason for failure.
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
            return (False, f"Player must activate a monster before benching {card_to_bench.title}.")
        
        # 4. Check if bench is already full.
        if len(player.bench) >= player.CONST_MAX_BENCH_CARDS:
            return (False, f"Player {player.title} bench is already full (max: {player.CONST_MAX_BENCH_CARDS}.)")
        
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
            is_legal, _ = RulesEngine._validate_bench_action(game_state, player, card.id)
            if is_legal:
                actions.append(
                    {
                        "type": "BENCH",
                        "payload": {"card_id": card.id, "card_title": card.title},
                    }
                )
                logger.debug(f"Legal action approved: BENCH for {card.title} ({card.id})")
        return actions

    @staticmethod
    def _validate_evolve_action(
        game_state, player, evo_card_id: int, base_monster_id: int
    ) -> tuple[bool, str | None]:
        """
        Validates if a specific evolve action is legal, returning a reason for failure.
        """
        # 1. Validate the evolution card from hand.
        evo_card = player.hand.get(evo_card_id)
        if not evo_card:
            return (False, f"Evolution card with ID {evo_card_id} not found in your hand.")
        if evo_card.card.type != CardType.MONSTER or evo_card.card.stage not in [
            StageType.STAGEONE,
            StageType.STAGETWO,
        ]:
            return (False, f"Card '{evo_card.title}' is not a valid evolution card.")

        # 2. Validate the base monster on the field.
        base_monster = None
        if player.active_monster and player.active_monster.id == base_monster_id:
            base_monster = player.active_monster
        else:
            base_monster = player.bench.get(base_monster_id)

        if not base_monster:
            return (False, f"Base monster with ID {base_monster_id} not found on your field.")

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
                is_legal, _ = RulesEngine._validate_evolve_action(
                    game_state, player, evo_card.id, base_monster.id
                )
                if is_legal:
                    actions.append(
                        {
                            "type": "EVOLVE",
                            "payload": {"evolution_card_id": evo_card.id, "base_monster_id": base_monster.id,},
                        }
                    )
        return actions

    @staticmethod
    def _get_retreat_actions(game_state, player) -> list:
        """
        Generates a list of legal RETREAT actions.
        A RETREAT action is possible if a player has an active monster that
        can pay the retreat cost and has space on the bench to retreat.
        """
        pass

    @staticmethod
    def _get_use_actions(game_state, player) -> list:
        pass
