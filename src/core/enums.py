from enum import Enum

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
    BASIC       = 'basic'
    STAGEONE    = 'stageone'
    STAGETWO    = 'stagetwo'
    EXRS        = 'exrs'
    EXBW        = 'exbw'
    EXSV        = 'exsv'
    MEGAEXXY    = 'megaexxy'
    MEGAEXSV    = 'megaexsv'
    TERA        = 'tera'

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

class RarityType(Enum):
    COMMON          = 'common'
    UNCOMMON        = 'uncommon'
    RARE            = 'rare'
    HOLO_RARE       = 'holo_rare'
    DOUBLE_RARE     = 'double_rare'
    ULTRA_RARE      = 'ultra_rare'
    SECRET_RARE     = 'secret_rare'
    ACE_SPEC_RARE   = 'ace_spec'
    ILLUSTRATION    = 'illustration'
    SPECIAL_ILL     = 'special_ill'
    HYPER_RARE      = 'hyper_rare'
    MEGA_HYPER_RARE = 'mega_hyper_rare'
    PROMO           = 'promo'