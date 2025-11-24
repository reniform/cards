from core.enums import ManaType, CardType
import random

# =====================================================================
# carddata.py is a bit of a scratch zone. Please deal.


BS_DOUBLE_COLORLESS_ENERGY_96 = {
    "type": CardType.MANA,
    "title": "Double Colorless Energy",
    "mana_type": ManaType.COLORLESS,
    "mana_val": 2
}
BS_FIGHTING_ENERGY_97 = {
    "type": CardType.MANA,
    "title": "Fighting Energy",
    "mana_type": ManaType.FIGHTING,
    "mana_val": 1
}
BS_FIRE_ENERGY_98 = {
    "type": CardType.MANA,
    "title": "Fire Energy",
    "mana_type": ManaType.FIRE,
    "mana_val": 1
}
BS_GRASS_ENERGY_99 = {
    "type": CardType.MANA,
    "title": "Grass Energy",
    "mana_type": ManaType.GRASS,
    "mana_val": 1
}
BS_LIGHTNING_ENERGY_100 = {
    "type": CardType.MANA,
    "title": "Lightning Energy",
    "mana_type": ManaType.LIGHTNING,
    "mana_val": 1
}
BS_PSYCHIC_ENERGY_101 = {
    "type": CardType.MANA,
    "title": "Psychic Energy",
    "mana_type": ManaType.PSYCHIC,
    "mana_val": 1
}
BS_WATER_ENERGY_102 = {
    "type": CardType.MANA,
    "title": "Water Energy",
    "mana_type": ManaType.WATER,
    "mana_val": 1
}

TEST_CARDS = [
    {"title": "Pikachu"},
    {"title": "Raichu"},
    {"title": "Venusaur"},
    {"title": "Ivysaur"},
    {"title": "Bulbasaur"},
    {"title": "Charmeleon"},
    #{"title": "Charmander"},
    {"title": "Charizard"},
]

def give_test_card(quantity: int):
    """
    Returns a list of monster titles for testing purposes.
    """
    deck_list = []
    for _ in range(quantity):
        card_title = random.choice(TEST_CARDS)["title"]
        deck_list.append(card_title)
    return deck_list

    # """
    # Generates a list of test card templates using the CardFactory.
    # """
    # templates = []
    # card_pool = [BULBASAUR_TEST_DATA, IVYSAUR_TEST_DATA, VENUSAUR_TEST_DATA,
    #              #BS_GRASS_ENERGY_99, BS_GRASS_ENERGY_99, BS_GRASS_ENERGY_99,
    #              BS_CHARMANDER_46, BS_CHARMANDER_46]
    # for i in range(quantity):
    #     # Cycle through the card pool to create a mixed deck
    #     card_data = card_pool[i % len(card_pool)]
    #     templates.append(CardFactory.create_card_from_db(**card_data))
    # return templates