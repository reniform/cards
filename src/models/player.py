import logging
import random

from core.enums import CardType, ManaType, StageType
from models.monster import MonsterCard

logger = logging.getLogger(__name__)


class PlayerUnit:
    """
    Manages the state and cards for a single player.

    This class holds all of a player's card zones (deck, hand, discard, etc.)
    and provides methods for game actions like drawing cards, playing monsters,
    and attaching mana.

    Attributes:
        title (str): The name of the player (e.g., "Player" or "Opponent").
        field (dict): A dictionary of all cards belonging to the player before
            being assigned to a specific zone.
        deck (dict): Cards currently in the player's deck.
        hand (dict): Cards currently in the player's hand.
        discard (dict): Cards in the player's discard pile.
        bench (dict): Monster cards on the player's bench.
        prize (dict): The player's prize cards.
        active_monster (MonsterCard): The monster currently in the active spot.
    """

    #! CONSTANTS
    CONST_MAX_CARDS = 60
    CONST_MAX_BENCH_CARDS = 5

    def __init__(self, title="Player"):
        """
        Initializes a PlayerUnit.

        Args:
            title (str): The name of the player.
        """
        self.title: str = title
        self.field: dict = {}
        self.deck: dict = {}
        self.hand: dict = {}
        self.discard: dict = {}
        self.bench: dict = {}
        self.prize: dict = {i: None for i in range(1, 7)}
        self.active_monster: MonsterCard = None

    #! FIELD METHODS
    def add_to_field(self, card) -> bool:
        """
        Adds a single card to the general field.

        The field is a collection of all cards belonging to a player before
        they are moved into specific zones like the deck or hand. This is an
        internal method that takes a card object.

        Args:
            card (Card): The card object to be added to the field. Before cards are moved to the deck, they are held in the field.
        """
        self.field[card.id] = card
        return True

    #! DECK METHODS
    def initialize_deck(self):
        """
        Populates the deck from the player's field of cards.
        Stops when the deck reaches the maximum allowed card count.
        """
        # Check for an already initialized deck.
        if self.deck:
            logger.warning("Deck is already initialized.")
            return

        # Attach field items to deck, stopping when the maximum is reached.
        for card_id, card in self.field.items():
            if len(self.deck) >= self.CONST_MAX_CARDS:
                break
            logger.debug(f"{card} added to deck for player {self.title}")
            self.deck[card_id] = card

    def shuffle_deck(self):
        """
        Performs a shuffle of the deck using `random.shuffle()`.
        """
        # Perform a check for an initialized deck.
        if not self.deck:
            logger.warning("Deck is not initialized.")
            return

        # Convert the dictionary's items to a list for shuffling.
        deck_items = list(self.deck.items())
        random.shuffle(deck_items)

        # Recreate the deck as a new dictionary with the shuffled order.
        self.deck = dict(deck_items)
        logger.info(f"Deck for {self.title} is shuffled.")

    def remove_from_deck(self, qty):
        """
        Removes and returns a specified number of cards from the deck (irrespective of ID).
        Functionally, cards are removed from the tail end of the deck.

        Args:
            qty (int): The number of cards to be removed.

        Returns:
            dict: A dictionary containing the removed card objects.
        """

        # Perform a check for an initialized deck.
        if not self.deck:
            print("Deck is not initialized.")
            return

        # Pop cards into a dict which we return.
        popped_cards = {}
        for i in range(qty):
            if not self.deck:
                print("Deck is empty.")
                break
            card_id, card = self.deck.popitem()
            popped_cards[card_id] = card
        return popped_cards

    #! HAND METHODS
    def add_to_hand(self, card):
        """
        Adds a card to the hand.
        This is an internal method that takes a card object.

        Args:
            card (Card): The card object to be added.

        Returns:
            bool: True, as adding to the hand is always successful.
        """
        self.hand[card.id] = card
        return True

    def remove_from_hand(self, card_id):
        """
        Removes and returns a card from the hand by its ID.

        Args:
            card_id (int): The ID of the card to be removed.

        Returns:
            Card: The removed card object, or None if not found.
        """
        return self.hand.pop(card_id, None)

    #! DECK -> HAND
    def draw_from_deck(self, qty=1):
        """
        Draws a specified number of cards from the deck and adds them to the hand.

        Args:
            qty (int): The number of cards to draw. Defaults to 1.

        Returns:
            bool: True if the draw was successful, False otherwise.
        """
        drawn_cards = self.remove_from_deck(qty)
        # Check for an empty deck
        if not drawn_cards:
            logger.warning(f"Deck for player {self.title} is empty.")
            return False
        for card in drawn_cards.values():
            self.add_to_hand(card)
            logger.debug(f"{card} drawn into player {self.title} hand.")
        return True

    #! DISCARD METHODS
    def add_to_discard(self, card):
        """
        Adds a card to the discard pile.
        This is an internal method that takes a card object.

        Args:
            card (Card): The card object to be discarded.

        Returns:
            bool: True, as adding to the discard pile is always successful.
        """
        self.discard[card.id] = card
        return True

    def remove_from_discard(self):
        pass

    #! BENCH METHODS
    def add_to_bench(self, card_id):
        """
        Adds a card to the bench **from the hand**.

        This is an external-facing method invoked by player action. It validates
        that the chosen card is a Basic Monster before moving it.

        Args:
            card_id (int): The ID of the card in the hand to move to the bench.
        """
        # Check against limit on amount of benched cards
        if len(self.bench) >= self.CONST_MAX_BENCH_CARDS:
            logger.warning("Too many cards in bench!")
            return False

        # Safely get the card from hand
        card_to_bench = self.hand.get(int(card_id))
        if not card_to_bench:
            logger.warning(f"Card with ID {card_id} not found in hand.")
            return False

        # Card must be a Basic Monster to be placed on the bench
        if card_to_bench.card.type != CardType.MONSTER:
            logger.warning(
                f"Cannot bench '{card_to_bench.title}': it is not a monster."
            )
            return False
        if card_to_bench.card.stage != StageType.BASIC:
            logger.warning(
                f"Cannot bench '{card_to_bench.title}': it is not a Basic monster."
            )
            return False

        self.bench[card_id] = card_to_bench
        self.remove_from_hand(card_id)
        logger.info(f"Benched {card_to_bench.title} for player {self.title}")
        return True

    def remove_from_bench(self, card_id) -> MonsterCard:
        """
        Removes and returns a card from the bench by its ID.

        Args:
            card_id (int): The ID of the card to remove.

        Returns:
            Card: The removed card object, or None if not found.
        """
        return self.bench.pop(card_id, None)

    #! ACTIVE MONSTER METHODS
    def set_active_monster(self, card_id):
        """
        Sets the active monster in the player's `active_monster` variable. The active monster is the chief actor in the player space, and is called upon to perform actions.
        This is an external-facing method that validates the chosen card is a
        Basic Monster from the hand.

        Args:
            card_id (int): The ID of the card in hand to set as active.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self.active_monster:
            logger.warning("Active monster already set (retreat your monster instead).")
            return False

        # Card must exist in hand
        card_to_activate = self.hand.get(card_id)
        if not card_to_activate:
            logger.warning(f"Card with ID {card_id} not found in hand.")
            return False

        # Card must be a Basic Monster
        if card_to_activate.card.type != CardType.MONSTER:
            logger.warning(
                f"Cannot activate '{card_to_activate.title}': it is not a monster."
            )
            return False
        if card_to_activate.card.stage != StageType.BASIC:
            logger.warning(
                f"Cannot activate '{card_to_activate.title}': it is not a Basic monster."
            )
            return False

        # Move the card from the hand to the active space
        self.active_monster = card_to_activate
        self.remove_from_hand(card_id)
        logger.info(
            f"{self.active_monster.card.title} is now set as active monster for player {self.title}"
        )
        return True

    #! MANA METHODS
    def add_mana(self, target, mana_type_str, qty=1):
        """
        Adds cheat mana to a monster's mana_pool.

        This is a test/debug method. The primary way to add mana should be
        by attaching ManaCards.

        Args:
            target (MonsterCard): The monster to add mana to.
            mana_type_str (str): The string representation of the mana type (e.g., "fire").
            qty (int): The amount of mana to add. Defaults to 1.
        """
        if not isinstance(target, MonsterCard):
            logger.warning("Target is not a monster!")
            return False
        try:
            mana_type = ManaType(mana_type_str.lower())
            target.mana_pool[mana_type] += qty
            logger.info(f"{qty} {mana_type_str} added to {target.title}")
            return True
        except (KeyError, ValueError):
            # Let the caller handle the error message
            return False

    def attach_mana(self, mana_card_id, target_monster_id):
        """
        Attaches a `ManaCard` from the hand to a target `MonsterCard` (active or bench).
        This is an external-facing method for a player action.

        Args:
            mana_card_id (int): The ID of the `ManaCard` in the player's hand.
            target_monster_id (int): The ID of the target `MonsterCard`.
        """
        # 1. Validate and retrieve the mana card from hand
        mana_card = self.hand.get(mana_card_id)
        if not mana_card or mana_card.card.type != CardType.MANA:
            logger.warning(f"Card ID {mana_card_id} is not a valid ManaCard in hand.")
            return False

        # Find the target monster (check active first, then bench)
        target_monster = None
        if self.active_monster and self.active_monster.id == target_monster_id:
            target_monster = self.active_monster
        else:
            target_monster = self.bench.get(target_monster_id)

        if not target_monster:
            logger.warning(f"Target monster with ID {target_monster_id} not found.")
            return False

        # Perform the move
        self.remove_from_hand(mana_card_id)
        target_monster.add_mana_attachment(mana_card)
        target_monster.has_attached = True
        return True

    #! UTILITY METHODS
    def use_utility_card(self, card_id, game_state):
        utility_card = self.hand.get(card_id)
        if not utility_card or utility_card.card.type != CardType.UTILITY:
            logger.warning(f"Card ID {card_id} is not a valid UtilityCard in hand.")
            return False

        effects_to_execute = self._get_card_effects(utility_card)

        for effect in effects_to_execute:
            # Pass the necessary context to the effect
            effect.execute(game_state, utility_card, self)

        self.remove_from_hand(card_id)
        self.add_to_discard(utility_card)
        logger.info(f"Player {self.title} used {utility_card.card.title}.")
        return True

    def _get_card_effects(self, card):
        """Extract relevant effects"""

        # Utility cards: just return their effects
        if card.card.type == CardType.UTILITY:
            return card.effects

        # Monster cards: depends... (codify later)
        elif card.type == CardType.MONSTER:
            return card.effects

    #! EVOLVE METHODS
    def evolve_monster(self, evo_card_id, base_card_id):
        # Get the evolution card from the hand.
        evo_card = self.hand.get(evo_card_id)
        if not evo_card:
            logger.warning(f"Evolution card with ID {evo_card_id} not found in hand.")
            return False

        # Find the base monster on the field (active or benched).
        base_card = None
        if self.active_monster and self.active_monster.id == base_card_id:
            base_card = self.active_monster
        else:
            base_card = self.bench.get(base_card_id)

        # Create the new monster.
        new_evo_card = MonsterCard(evo_card.card)

        # Transfer the battle state.
        # damage = the base card data's base health - live card's current health
        damage_taken = base_card.card.health - base_card.health
        new_evo_card.health = new_evo_card.card.health - damage_taken
        new_evo_card.attached_mana = base_card.attached_mana

        # Attach the base card and its entire history to the new evo card.
        new_evo_card.prior_evos.append(base_card)
        new_evo_card.prior_evos.extend(base_card.prior_evos)

        # Swap the cards on the field.
        if self.active_monster and self.active_monster.id == base_card_id:
            self.active_monster = new_evo_card
        else:
            # The base card must be on the bench, so replace it there.
            del self.bench[base_card_id]
            self.bench[new_evo_card.id] = new_evo_card

        # Cleanup.
        self.remove_from_hand(evo_card_id)
        new_evo_card.has_evolved = True
        logger.info(f"{base_card.title} evolved into {new_evo_card.title}!")
        return True

    #! OTHER METHODS
    def reset(self):
        """
        Resets the player's state to its initial condition.
        Clears all game zones like hand, deck, discard, etc.
        """
        logger.info(f"Resetting state for player: {self.title}")
        self.field = {}
        self.deck = {}
        self.hand = {}
        self.discard = {}
        self.bench = {}
        self.prize = {i: None for i in range(1, 7)}
        self.active_monster = None
