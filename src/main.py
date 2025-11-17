from core.game import GameState
from models.player import PlayerUnit
from core.carddata import give_test_card
from core.enums import CardType
from models.monster import MonsterTemplate, MonsterCard
from models.utility import UtilityTemplate, UtilityCard
from models.mana import ManaTemplate, ManaCard

import colorlog
import logging
logger = logging.getLogger(__name__)

def setup_logging():
    """
    Configures a colored logger for the application.
    """
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s %(purple)s[%(name)s]%(reset)s %(blue)s%(message)s',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red,bg_white',
        }
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

def generate_deck_from_list(deck_list, player_unit):
    """
    Populates a player's card field from a list of card data dictionaries.
    """
    for card_data in deck_list:
        match card_data['type']:
            case CardType.MONSTER:
                template = MonsterTemplate(**card_data)
                player_unit.add_to_field(MonsterCard(template))
            case CardType.UTILITY:
                template = UtilityTemplate(**card_data)
                player_unit.add_to_field(UtilityCard(template))
            case CardType.MANA:
                template = ManaTemplate(**card_data)
                player_unit.add_to_field(ManaCard(template))

def main():
    """
    Main entry point for the application. Sets up the game and starts the engine.
    """
    setup_logging()
    logger.info('Starting cards!')
    # 1. Create players
    player = PlayerUnit()
    opponent = PlayerUnit('Opponent')

    # 2. Generate and setup decks
    generate_deck_from_list(give_test_card(100), player_unit=player)
    generate_deck_from_list(give_test_card(100), player_unit=opponent)

    player.initialize_deck()
    player.shuffle_deck()
    opponent.initialize_deck()
    opponent.shuffle_deck()

    # 3. Draw starting hands
    player.draw_from_deck(7)
    opponent.draw_from_deck(7)

    # Pre-activate an opponent monster for testing purposes.
    for card_id, card in opponent.hand.items():
        if card.card.type == CardType.MONSTER:
            opponent.set_active_monster(card_id)
            # This break ensures we only activate the first monster found.
            break

    # 4. Create and run the game state
    game = GameState(player, opponent)
    game.run()

if __name__ == "__main__":
    main()