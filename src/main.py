import logging

import colorlog

from controller.game_controller import GameController
from core.card_factory import CardFactory
from core.carddata import give_test_card
from core.game import GameState
from database.card_repository import CardRepository
from models.monster import MonsterCard, MonsterTemplate
from models.player import PlayerUnit
from termio.view import TerminalView

logger = logging.getLogger(__name__)


def setup_logging():
    """
    Configures a colored logger for the application.
    """
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s %(purple)s[%(name)s]%(reset)s %(blue)s%(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_white",
        },
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)


def generate_deck_from_list(deck_list, player_unit):
    """
    Populates a player's card field from a list of card data.
    The list can contain either card data dictionaries or pre-instantiated card objects.
    """
    card_repo = CardRepository()
    for card_data in deck_list:
        title = card_data
        set_code = "BS"  # Default set_code for test data
        template = CardFactory.create_card_from_db(card_repo, title, set_code)

        if not template:
            logger.warning(f"Could not create card for {title} ({set_code})")
            continue

        if isinstance(template, MonsterTemplate):
            player_unit.add_to_field(MonsterCard(template))
        # Add cases for UTILITY and MANA here if needed.


def main() -> None:
    """
    Main entry point for the application. Sets up the game and starts the engine.
    """
    setup_logging()
    logger.info("starting blackstar! v0.1.0")
    # 1. Create players
    player = PlayerUnit(title="Player")
    opponent = PlayerUnit(title="Opponent")

    # Define a specific deck list for the player for targeted testing.
    # The `generate_deck_from_list` function will take these titles
    # and fetch their full data from the database.
    player_deck_list = [
        "Pikachu", "Raichu"
    ] * 12

    # Generate and setup decks.
    generate_deck_from_list(player_deck_list, player_unit=player)
    generate_deck_from_list(give_test_card(60), player_unit=opponent) # Opponent can still use a random deck

    player.initialize_deck()
    player.shuffle_deck()
    opponent.initialize_deck()
    opponent.shuffle_deck()

    player.set_prize_cards(6)
    opponent.set_prize_cards(6)

    player.draw_from_deck(7)
    opponent.draw_from_deck(7)

    # Handle mulligans if no basic monster is in the opening hand.
    while not player.has_basic_monster_in_hand():
        logger.warning(f"{player.title} has no basic monster, redrawing hand.")
        player.return_hand_to_deck()
        player.shuffle_deck()
        player.draw_from_deck(7)

    while not opponent.has_basic_monster_in_hand():
        logger.warning(f"{opponent.title} has no basic monster, redrawing hand.")
        opponent.return_hand_to_deck()
        opponent.shuffle_deck()
        opponent.draw_from_deck(7)

    # Create and run the game state.
    game_state = GameState(player, opponent)
    # Manually trigger the start-of-turn logic for the first player.
    game_state._start_new_turn_for_player()

    terminal_view = TerminalView()
    game_controller = GameController(game_state, terminal_view)
    game_controller.run()


if __name__ == "__main__":
    main()
