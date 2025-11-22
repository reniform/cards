from .connection import get_db_connection
from models.monster import MonsterTemplate

# from models.monster import AbilityTemplate # Uncomment when AbilityTemplate is created

from core.enums import ManaType, StageType


class CardRepository:
    """
    The repository for all database operations related to fetching and assembling card data.
    This class acts as a bridge between the raw database and the application's object models.
    """

    def __init__(self):
        """Initializes the repository with a database connection."""
        self.conn = get_db_connection()

    def get_card_data_as_kwargs(self, title: str, set_code: str) -> dict | None:
        """
        Fetches all data for a single conceptual card and assembles it into a template object.

        Args:
            title: The title of the card (e.g., "Charizard").
            set_code: The original set code of the card (e.g., "BS").

        Returns:
            A fully populated MonsterTemplate, UtilityTemplate, or ManaTemplate object,
            or None if the card is not found.
        """
        cursor = self.conn.cursor()

        # --- Fetch the base conceptual card data ---
        # Find the card in the `cards` table to get its ID and primary details.
        # If not found, we can return None immediately.
        cursor.execute(
            """SELECT id, title, card_type, subtype FROM cards WHERE title = ? AND set_code = ?""",
            (title, set_code),
        )

        card_data = cursor.fetchone()
        if not card_data:
            return None

        card_id = card_data["id"]
        card_type = card_data["card_type"]

        #! MONSTER HANDLING
        # --- Fetch all related "many-to-one" and "one-to-one" data ---
        if card_type == "MONSTER":
            # -- Get monster stats from `monsters` table (one-to-one).
            cursor.execute(
                """SELECT card_id, stage, health, retreat_cost FROM monsters WHERE card_id = ?""",
                (card_id,),
            )
            monster_data = cursor.fetchone()

            # -- Get dex data from `pokedex_entries` table (one-to-one).
            cursor.execute(
                """SELECT card_id, level, dex_number, species, height_ft_in, height_m, weight_lbs, weight_kg, dex_entry FROM pokedex_entries WHERE card_id = ?""",
                (card_id,),
            )
            pokedex_data = cursor.fetchone()

            # -- Get all types from `monster_types` (many-to-many).
            cursor.execute(
                """SELECT card_id, mana_type FROM monster_types WHERE card_id = ?""",
                (card_id,),
            )
            type_data = cursor.fetchall()

            # - Get all weaknesses from `monster_weaknesses` (many-to-many).
            cursor.execute(
                """SELECT card_id, mana_type, modifier FROM monster_weaknesses WHERE card_id = ?""",
                (card_id,),
            )
            weakness_data = cursor.fetchall()

            # - Get all resistances from `monster_resistances` (many-to-many).
            cursor.execute(
                """SELECT card_id, mana_type, modifier FROM monster_resistances WHERE card_id = ?""",
                (card_id,),
            )
            resistance_data = cursor.fetchall()

            # - Get all evolution sources from `monster_evolutions` (many-to-many).
            cursor.execute(
                """SELECT card_id, evolves_from_name FROM monster_evolutions WHERE card_id = ?""",
                (card_id,),
            )
            evolution_data = cursor.fetchall()

            # - Get all abilities from `monster_abilities` (many-to-many).
            cursor.execute(
                """SELECT id, card_id, name, type, description FROM monster_abilities WHERE card_id = ?""",
                (card_id,),
            )
            ability_data = cursor.fetchall()

            # - Get all attacks from `attacks` (many-to-many).
            cursor.execute(
                """SELECT id, card_id, title, damage, description FROM attacks WHERE card_id = ?""",
                (card_id,),
            )
            attack_data = cursor.fetchall()

            # For each ability and attack found, we need to fetch their associated effects and costs.
            attacks = []
            for attack_row in attack_data:
                attack_id = attack_row["id"]

                # - For each attack_id, get costs from `attack_costs`.
                cursor.execute(
                    """SELECT attack_id, mana_type, quantity FROM attack_costs WHERE attack_id = ?""",
                    (attack_id,),
                )
                cost_data = cursor.fetchall()

                # - For each attack_id, get effects from `effects`.
                cursor.execute(
                    """SELECT id, source_card_id, source_attack_id, effect_name, target, value, condition, execution_order FROM effects WHERE source_attack_id = ?""",
                    (attack_id,),
                )
                effect_data = cursor.fetchall()

                attacks.append(
                    {
                        "details": attack_row,
                        "costs": cost_data,
                        "effects": effect_data,
                    }
                )

            abilities = []
            for ability_row in ability_data:
                ability_id = ability_row["id"]

                # - For each ability_id, get effects from `effects`.
                cursor.execute(
                    """SELECT id, source_card_id, source_ability_id, effect_name, target, value, condition, execution_order FROM effects WHERE source_ability_id = ?""",
                    (ability_id,),
                )
                effect_data = cursor.fetchall()

                abilities.append({"details": ability_row, "effects": effect_data})
            
            # --- Step 5: Assemble the Template Object ---
            # With all the data now in memory, create an instance of MonsterTemplate
            # (or another template type) and populate it before returning.

            # First, process the raw attack data into a list of dictionaries
            # that can be passed to the Attack class constructor.
            attack_kwargs_list = []
            for attack in attacks:
                # The Attack class expects a flat dictionary of its parameters.
                # We combine the 'details' with the 'costs' and 'effects'.
                attack_details = dict(attack["details"])
                # Convert the list of cost dicts into a single dict mapping ManaType to quantity.
                attack_details["cost"] = {
                    ManaType(cost["mana_type"].lower()): cost["quantity"] for cost in attack["costs"]
                }
                attack_details["effects"] = [dict(effect) for effect in attack["effects"]]
                attack_kwargs_list.append(attack_details)

            # TODO: Process abilities into AbilityTemplate objects once the class is created.
            # For now, we will pass the raw data.
            # ability_templates = []
            # for ability in abilities:
            #     ... create AbilityTemplate objects ...
            #     ability_templates.append(ability_template)

            monster_kwargs = {
                "title": card_data["title"],
                "type": card_data["card_type"],
                "stage": monster_data["stage"] if monster_data else None,
                "health": monster_data["health"] if monster_data and monster_data.get("health") is not None else 0,
                "retreat_val": monster_data["retreat_cost"] if monster_data and monster_data.get("retreat_cost") is not None else 0,
                "level": pokedex_data.get("level"),
                "dex_data": dict(pokedex_data) if pokedex_data else {},
                "mana_type": type_data[0]["mana_type"] if type_data else "COLORLESS",
                "weak_type": weakness_data[0]["mana_type"] if weakness_data else None,
                "weak_mult": weakness_data[0]["modifier"] if weakness_data else None,
                "resist_type": resistance_data[0]["mana_type"] if resistance_data else None,
                "resist_val": resistance_data[0]["modifier"] if resistance_data else None,
                "evolve_from": evolution_data[0]["evolves_from_name"] if evolution_data else None,
                "abilities": abilities,
                "attacks": attack_kwargs_list,
            }

            return monster_kwargs
