import logging

from core.rules import RulesEngine
from models.player import PlayerUnit
from core.coins import coin

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, player, opponent):
        self.player1 = player
        self.player2 = opponent
        self.turn_count = 1
        self.active_player = self.player1
        self.current_phase = "main"
        self.legal_actions = []
        self.legal_action_types = set()
        self.winner = None

    @property
    def waiting_player(self) -> PlayerUnit:
        """A property to easily get the player who is not active."""
        return self.player2 if self.active_player is self.player1 else self.player1

    @property
    def current_player(self) -> PlayerUnit:
        """A property to easily get the player whose turn it currently is."""
        return self.active_player

    def get_legal_actions(self, player: PlayerUnit) -> list:
        """Retrieves the list of legal actions from the rules engine (see rules.py)."""
        return RulesEngine.get_legal_actions(self, player)

    def next_turn(self) -> None:
        """
        Handles all end-of-turn and start-of-turn logic.
        This includes swapping the active player and drawing a card for the new player.
        """        
        self.active_player = self.waiting_player
        self.turn_count += 1
        self._start_new_turn_for_player()

    def _start_new_turn_for_player(self):
        """Handles all logic that occurs at the very beginning of a player's turn."""

        # Check for status conditions
        if self.active_player.active_monster:
            if "POISONED" in self.active_player.active_monster.special_conditions:
                logger.info(
                    f"Adding 10 damage for POISONED {self.active_player.active_monster}"
                )
                self.active_player.active_monster.take_damage(10)
            if "POISONED_20" in self.active_player.active_monster.special_conditions:
                logger.info(
                    f"Adding 20 damage for badly POISONED {self.active_player.active_monster}"
                )
                self.active_player.active_monster.take_damage(20)
            if "BURNED" in self.active_player.active_monster.special_conditions:
                logger.info(
                    f"Adding 20 damage for BURNED {self.active_player.active_monster}"
                )
                self.active_player.active_monster.take_damage(20)
                logger.info(
                    f"Flipping a coin for BURNED {self.active_player.active_monster}"
                )
                if coin():
                    logger.info(
                        f"HEADS {self.active_player.active_monster} has recovered from BURNED."
                    )
                    del self.active_player.active_monster.special_conditions["BURNED"]
                else:
                    logger.info(
                        f"TAILS: {self.active_player.active_monster} remains BURNED."
                    )
            if "ASLEEP" in self.active_player.active_monster.special_conditions:
                logger.info(
                    f"Flipping a coin for ASLEEP {self.active_player.active_monster}"
                )
                if coin():
                    logger.info(
                        f"HEADS: {self.active_player.active_monster} has recovered from ASLEEP."
                    )
                    del self.active_player.active_monster.special_conditions["ASLEEP"]
                else:
                    logger.info(
                        f"TAILS: {self.active_player.active_monster} remains ASLEEP."
                    )
            if "PARALYZED" in self.active_player.active_monster.special_conditions:
                logger.info(f"Removing PARALYZED from {self.active_player.active_monster}")
                del self.active_player.active_monster.special_conditions["PARALYZED"]

        # Reset monster card flags for the new active player.
        if self.active_player.active_monster:
            self.active_player.active_monster.has_attacked = False
            self.active_player.active_monster.has_attached = False
            self.active_player.active_monster.has_evolved = False
            self.active_player.active_monster.is_immune = False

        for monster in self.active_player.bench.values():
            monster.has_attacked = False
            monster.has_attached = False
            monster.has_evolved = False
            monster.is_immune = False

    def _handle_knockout(self, knocked_out_player: PlayerUnit):
        """
        Handles the entire sequence of a monster being knocked out.
        """
        # 1. Announce the knockout.
        fainted_monster = knocked_out_player.active_monster
        logger.info(f"{fainted_monster.title} for {knocked_out_player.title} has been knocked out!")

        # 2. Move the fainted monster and all its attachments to the discard pile.
        # Discard attached mana.
        for mana_card in fainted_monster.attached_mana.values():
            knocked_out_player.add_to_discard(mana_card)
        # Discard prior evolutions.
        for evo_card in fainted_monster.prior_evos:
            knocked_out_player.add_to_discard(evo_card)
        # Finally, discard the monster itself.
        knocked_out_player.add_to_discard(fainted_monster)

        # 3. Clear the active monster slot.
        knocked_out_player.active_monster = None

        # 4. The opponent takes a prize card.
        # We will need a new command for the player to choose which prize card.
        # For now, we'll log it and set a flag.
        prize_taker = self.player1 if knocked_out_player is self.player2 else self.player2
        logger.info(f"{prize_taker.title} gets to take a prize card!")
        # TODO: Implement a "take_prize" command and a game state flag.
        # For now, let's automatically take the first available prize for testing.
        if prize_taker.prize:
            first_prize_slot = next(iter(prize_taker.prize))
            prize_taker.take_prize_card(first_prize_slot)

        # 5. Check for win condition (no more prize cards).
        if not prize_taker.prize:
            logger.info(f"{prize_taker.title} has taken all their prize cards! They win!")
            self.winner = prize_taker

        # 6. The player with the knocked-out monster must promote a new one.
        if not knocked_out_player.bench:
            logger.info(f"{knocked_out_player.title} has no benched monsters to promote.")
            logger.info(f"Game over!!! {prize_taker.title} wins!")
            self.winner = prize_taker
        else:
            logger.info(f"{knocked_out_player.title} must choose a new active monster from their bench.")
            # TODO: Force the player to use a "promote" command.

    def check_knockouts(self):
        """Checks both players for knocked out monsters."""
        if self.player1.active_monster and self.player1.active_monster.health <= 0:
            self._handle_knockout(self.player1)
        if self.player2.active_monster and self.player2.active_monster.health <= 0:
            self._handle_knockout(self.player2)

    