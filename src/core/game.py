import logging
import os

import colorful as cf

from core.enums import CardType, StageType
from termio.termio import CommandHandler
from termio.view import TerminalView

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

    @property
    def waiting_player(self):
        """A property to easily get the player who is not active."""
        return self.player2 if self.active_player is self.player1 else self.player1
    
    def get_legal_actions(self, player) -> list:
        """
        Constructs a list of all valid actions a player can take.
        """
        legal_actions = []

        # --- Check: Can the player PASS? ---
        # (Almost always yes during their turn.)
        legal_actions.append({"type": "PASS"})
        logger.debug(f'Legal action approved: PASS for {player.title}')

        # --- Check: Can the player ATTACK? ---
        # Player who goes first cannot attack on their first turn (turn_count == 1).
        # For target discovery, see get_valid_targets() below.
        if self.turn_count > 1:
            attack_actions = self._get_attack_actions(player, self.waiting_player)
            legal_actions.extend(attack_actions)

        # --- Check: Can the player ACTIVATE a monster? ---
        activate_actions = self._get_activate_actions(player)
        legal_actions.extend(activate_actions)

        #  --- Check: Can the player ATTACH mana?
        # The rule is one mana attachment per turn.
        attach_actions = self._get_attach_actions(player)
        legal_actions.extend(attach_actions)

        return legal_actions
    
    def _get_attack_actions(self, player, opponent) -> list:
        actions = []
        attacker = player.active_monster

        # Check if active mon exists or has attacked before
        if attacker is None or attacker.has_attacked:
            return actions
        
        # Get valid targets.
        valid_targets = [opponent.active_monster]
        # Later with bench sniping: valid_targets.extend(opponent.bench)

        # Iterate through each attack to see if it's usable
        for i, attack in enumerate(attacker.card.attacks):
            # Check if the monster has enough mana for this specific attack
            if player.active_monster.has_mana(attack.cost):
                # If affordable, create an action for each valid target
                for target in valid_targets:
                    if target: # Ensure target exists
                        actions.append({
                            "type": "ATTACK",
                            "payload": {
                                "attack_name": attack.title,
                                "attack_index": i,
                                "target": target,
                                "target_id": target.id
                            }
                        })
                        logger.debug(f"Legal action approved: ATTACK '{attack.title}' on target {target.id} for {player.title}")
        return actions

    def _get_activate_actions(self, player) -> list:
        """
        Generates a list of legal ACTIVATE actions.
        An ACTIVATE action is possible if the player has no active monster
        and has a Basic Monster in their hand.
        """
        actions = []
        # If there's already an active monster, no activation is possible.
        if player.active_monster:
            return actions
        
        # Look through the hand for valid monsters to activate.
        for card in player.hand.values():
            if card.card.type == CardType.MONSTER and card.card.stage == StageType.BASIC:
                actions.append({
                    "type": "ACTIVATE",
                    "payload": {"card_id": card.id, "card_title": card.title}
                })
                logger.debug(f"Legal action approved: ACTIVATE for {card.title} ({card.id})")
        return actions

    def _get_attach_actions(self, player) -> list:
        """
        Generates a list of legal ATTACH actions.
        An ATTACH action is possible if the player has a monster to attach
        a mana card to, with one mana attachment per monster allowed.
        The player can only attach one mana card per monster per turn.
        """
        actions = []

        # Find all mana cards in the player's hand.
        mana_in_hand = [card for card in player.hand.values() if card.card.type == CardType.MANA]
        if not mana_in_hand:
            return actions

        # Find all possible monster targets that haven't had mana attached this turn.
        possible_targets = []
        if player.active_monster and not player.active_monster.has_attached:
            possible_targets.append(player.active_monster)
        for monster in player.bench.values():
            if not monster.has_attached:
                possible_targets.append(monster)

        # Create an action for every combination of mana card and valid target.
        for mana_card in mana_in_hand:
            for target_monster in possible_targets:
                actions.append({
                    "type": "ATTACH",
                    "payload": {
                        "mana_card_id": mana_card.id,
                        "target_monster_id": target_monster.id
                    }
                })
        return actions


    def next_turn(self) -> None:
        """
        Handles all end-of-turn and start-of-turn logic.
        This includes swapping the active player and drawing a card for the new player.
        """
        # Swap the active player.
        # TODO: IMPLEMENT SWITCH FOR SINGLE OR MULTI ONCE HEURISTICS MODEL IS UP
        self.active_player = self.waiting_player
        self.turn_count += 1

        # Reset monster card flags.
        if self.active_player.active_monster:
            self.active_player.active_monster.has_attacked = False
            self.active_player.active_monster.has_attached = False
        for monster in self.active_player.bench:
            monster.has_attacked = False
            monster.has_attached = False
        
        # The new active player draws a card.
        if len(self.active_player.deck) > 0:
            self.active_player.draw_from_deck(1)

    def redraw_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self.legal_actions) # Keep this for debugging

        print(f'\n== {cf.bold} Turn [{self.turn_count}] {cf.reset} ======================================================================')
        print(TerminalView.print_player_data(self.waiting_player, opposite=True))
        print(TerminalView.print_bench(self.waiting_player))
        print(TerminalView.print_active_monster(self.waiting_player))
        print(TerminalView.print_active_monster(self.active_player, Bold=True))
        print(TerminalView.print_bench(self.active_player))
        print(TerminalView.print_player_data(self.active_player))
        print(TerminalView.print_hand(self.active_player))
        print(TerminalView.print_prompt(self.legal_action_types))

    def run(self) -> None:
        """
        The main game loop.
        """
        while True:
            # 1. Calculate all legal actions for the current state.
            self.legal_actions = self.get_legal_actions(self.active_player)
            self.legal_action_types = {action['type'] for action in self.legal_actions}
            
            # 2. Redraw the screen with the new state.
            self.redraw_screen()
            command = input(f"[{self.active_player.title}] perform an action! ==> ")

            parts = command.split()
            if not parts:
                continue

            command_word = parts[0]
            args = parts[1:]

            if command_word == 'debug': # Special case to break the loop
                break
            elif handler := CommandHandler.COMMANDS.get(command_word):
                # Pass the whole game state to the handler
                turn_ended, needs_redraw = handler(self, *args)
                if turn_ended:
                    self.next_turn()
                # The loop will automatically redraw on the next iteration.

            else:
                print("??? What???")
        
            # PERFORM CHECKS
            if self.waiting_player.active_monster and self.waiting_player.active_monster.health <= 0:
                print("You win!")
                os._exit(1)