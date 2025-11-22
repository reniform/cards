from models.monster import MonsterTemplate
from core.enums import CardType, ManaType, StageType

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
        if "weak_type" in kwargs and isinstance(kwargs, str):
            kwargs["weak_type"] = ManaType(kwargs["weak_type"].lower())

        # -- "resist_type" to ManaType --
        if "resist_type" in kwargs and isinstance(kwargs["resist_type"], str):
            kwargs["resist_type"] = ManaType(kwargs["resist_type"].lower())

        # See Attack class in combat.py for attack handling kwarg arguments.
        return MonsterTemplate(**kwargs)
    
    @classmethod
    def create_card_from_db(cls, card_repo, title: str, set_code: str):
        """
        Creating a card template from a CardRepository (see card_repository.db).
        """

        # Assuming the repository will return a dict ...
        card_data = card_repo.get_card_data_as_kwargs(title, set_code)

        if card_data and CardType(card_data.get("type")) == CardType.MONSTER:
            return cls.create_monster_template(**card_data)
        else:
            pass # INclude UTILITY and MANA logic.