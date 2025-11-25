from typing import TYPE_CHECKING
from .base_command import Command
from models.monster import MonsterCard
from models.utility import UtilityCard
from models.mana import ManaCard

if TYPE_CHECKING:
    from core.game import GameState


class InspectCommand(Command):
    """
    A command to display detailed information about a specific card.
    """

    def __init__(self, card_id: int):
        """
        Initializes the InspectCommand.

        Args:
            card_id: The unique ID of the card to inspect.
        """
        self.card_id = card_id

    def execute(self, game_state: "GameState") -> tuple[bool, bool]:
        """
        Finds the card across all game zones and prints its details.
        This is a meta-action and does not affect the game state.
        """
        card_to_inspect = None

        # Search all players and all zones for the card
        for p in [game_state.current_player, game_state.waiting_player]:
            if self.card_id in p.hand:
                card_to_inspect = p.hand[self.card_id]
                break
            if p.active_monster and p.active_monster.id == self.card_id:
                card_to_inspect = p.active_monster
                break
            if self.card_id in p.bench:
                card_to_inspect = p.bench[self.card_id]
                break

        if not card_to_inspect:
            print(f"Card with ID {self.card_id} not found on the field or in any hand.")
            return False, False

        # --- MonsterCard Inspection ---
        if isinstance(card_to_inspect, MonsterCard):
            card = card_to_inspect.card  # This is the MonsterTemplate
            print(
                "\n"
                + "=" * 20
                + f" Inspecting: {card.title} (ID: {card_to_inspect.id}) "
                + "=" * 20
            )
            print(
                f"  - Type: {card.mana_type.value} | Stage: {card.stage.value} | HP: {card_to_inspect.health}/{card.health}"
            )
            print(f"  - Evolves From: {card.evolve_from or 'N/A'}")
            print(
                f"  - Weakness: {card.weak_type.value if card.weak_type else 'N/A'} (x{card.weak_mult or '0'})"
            )
            print(
                f"  - Resistance: {card.resist_type.value if card.resist_type else 'N/A'} (-{card.resist_val or '0'})"
            )
            print(f"  - Retreat Cost: {card.retreat_val}")
            print("\n  --- Attacks ---")
            if card.attacks:
                for i, attack in enumerate(card.attacks):
                    cost_str = ", ".join(
                        [
                            f"{quantity} {mana_type.name}"
                            for mana_type, quantity in attack.cost.items()
                        ]
                    )
                    print(
                        f"    {i}: {attack.title} | Damage: {attack.damage} | Cost: [{cost_str}]"
                    )
                    if attack.description:
                        print(f"       {attack.description}")
                    if attack.effects:
                        for effect in attack.effects:
                            print(f"         - Effect: {effect._raw_data}")
            else:
                print("    - No attacks.")

        # --- UtilityCard Inspection ---
        elif isinstance(card_to_inspect, UtilityCard):
            card = card_to_inspect.card
            print(
                "\n"
                + "=" * 20
                + f" Inspecting: {card.title} (ID: {card_to_inspect.id}) "
                + "=" * 20
            )
            print(f"  - Type: {card.type.value}")
            print(f"  - Description: {card.description}")

        # --- ManaCard Inspection ---
        elif isinstance(card_to_inspect, ManaCard):
            card = card_to_inspect.card
            print(
                "\n"
                + "=" * 20
                + f" Inspecting: {card.title} (ID: {card_to_inspect.id}) "
                + "=" * 20
            )
            print(f"  - Type: {card.type.value}")
            print(f"  - Mana Type: {card.mana_type.name}")
            print(f"  - Mana Value: {card.mana_val}")

        else:
            print(
                f"Inspection not fully supported for card type: {type(card_to_inspect)}."
            )

        print("=" * (42 + len(card.title) + len(str(card_to_inspect.id))) + "\n")

        input("(press enter to continue)")
        # This action doesn't end the turn, but requires a redraw to clear the inspection text.
        return False, True
