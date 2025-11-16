from cards.game import GameState
from models.player import PlayerUnit
from cards.carddata import give_test_card
from cards.enums import CardType
from models.monster import MonsterTemplate, MonsterCard
from models.utility import UtilityTemplate, UtilityCard
from models.mana import ManaTemplate, ManaCard

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

    # 4. Create and run the game state
    game = GameState(player, opponent)
    game.run()

if __name__ == "__main__":
    main()