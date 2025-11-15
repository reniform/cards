from enum import Enum

"""
'enums.py' contains enumerations and basic game data.
"""

class CardType(Enum):
    """
    'CardType' lists the types of cards available to the player.
    """
    MONSTER = 'monster'
    UTILITY = 'utility'
    MANA    = 'mana'

class StageType(Enum):
    """
    'StageType' lists the stages in incremental order.
    """
    BASIC    = 2
    STAGEONE = 3
    STAGETWO = 4

class ManaType(Enum):
    """
    'ManaType' lists the categories of mana available in the game.
    """
    GRASS       = 'grass'
    FIRE        = 'fire'
    WATER       = 'water'
    LIGHTNING   = 'lightning'
    FIGHTING    = 'fighting'
    PSYCHIC     = 'psychic'
    DARKNESS    = 'darkness'
    METAL       = 'metal'
    DRAGON      = 'dragon'
    FAIRY       = 'fairy'
    COLORLESS   = 'colorless'