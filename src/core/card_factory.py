from models.monster import MonsterTemplate
from core.enums import CardType, ManaType, StageType
from database.card_repository import CardRepository

class CardFactory:
    """
    This factory creates card template objects from raw kwargs data from the SQL
    database. This is the single point of entry for card creation.
    """

    @staticmethod
    def create_monster_template(**kwargs) -> MonsterTemplate:
        """
        Assembles a MonsterType from a dictionary of arguments.
        """

        # Convert string representations to enums (CardType, ManaType, StageType).
        # --- "type" to CardType ---
        type_str = kwargs.get("type", "monster")
        # Ensure we handle both string ("MONSTER") and enum (CardType.MONSTER) inputs safely.
        kwargs["type"] = CardType(type_str.value if isinstance(type_str, CardType) else type_str.lower())

        # --- "stage" to StageType ---
        if "stage" in kwargs and isinstance(kwargs["stage"], str):
            kwargs["stage"] = StageType(kwargs["stage"].lower())
        
        # -- "mana_type" to ManaType ---
        if "mana_type" in kwargs and isinstance(kwargs["mana_type"], str):
            kwargs["mana_type"] = ManaType(kwargs["mana_type"].lower())

        # -- "weak_type" to ManaType ---
        if "weak_type" in kwargs and isinstance(kwargs["weak_type"], str):
            kwargs["weak_type"] = ManaType(kwargs["weak_type"].lower())
        # -- bonus mission: strip 'x' from 'weak_mult'
        if "weak_mult" in kwargs and isinstance(kwargs["weak_mult"], str):
            kwargs["weak_mult"] = int(kwargs["weak_mult"].replace("x", ""))

        # -- "resist_type" to ManaType --
        if "resist_type" in kwargs and isinstance(kwargs["resist_type"], str):
            kwargs["resist_type"] = ManaType(kwargs["resist_type"].lower())
        #  -- bonus mission: strip '-' from 'resist_val'
        if "resist_val" in kwargs and isinstance(kwargs["resist_val"], str):
            kwargs["resist_val"] = int(kwargs["resist_val"].replace("-", ""))

        # See Attack class in combat.py for attack handling kwarg arguments.
        return MonsterTemplate(**kwargs)
    
    @classmethod
    def create_card_from_db(cls, card_repo: CardRepository, title: str, set_code: str):
        """
        Creating a card template from a CardRepository (see card_repository.db).
        """

        # Assuming the repository will return a dict ...
        card_data = card_repo.get_card_data_as_kwargs(title=title, set_code=set_code)
        if not card_data:
            return None

        card_type = CardType(card_data.get("type").lower())
        if card_type == CardType.MONSTER:
            return cls.create_monster_template(**card_data)
        elif card_type == CardType.UTILITY:
            pass
        elif card_type == CardType.MANA:
            pass