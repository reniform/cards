import logging

from core.combat import Attack
from core.enums import CardType, ManaType, StageType
from effects.effects import EffectRegistry

from .card import CardTemplate

logger = logging.getLogger(__name__)


class MonsterTemplate:
    """
    Immutable instance and static data source for monster cards.

    Attributes:
        type (CardType): `MonsterCards` are all type `MONSTER`.
        id (int): A card's unique ID is created during instantiation at `__init__()`.
        title (str): Necessary. The name of the monster.
        stage (StageType): Necessary. The monster's stage (basic, stage 1, stage 2, mega/ex/etc).
        mana_type (ManaType): Necessary. The mana type assigned to the monster.
        evolve_to (str): Necessary. The monster from which this current monster evolves from.
        evolve_from (str): Necessary. The monster to which this current monster evolves from.
        health (int): Necessary. Base value for the monster's health.
        weak_type (ManaType): Necessary. The mana type to which the monster is weak to.
        weak_mult (int): Necessary. The value by which weakness is multiplied.
        resist_type (ManaType): Necessary. The mana type to which the monster is resistant to.
        resist_val (int): Necessary. The value by which resistance is multiplied.
        retreat_val (int): Necessary. The monster's retreat cost.
        attacks (list): Necessary. A list of attacks, each their own dictionary.
        abilities (list): Optional. A list of abilities, each their own dictionary.
        level (int): Optional. The monster's level as printed on the card.
        dex_data (dict): A dictionary of monster information received by the metadata handler as printed on the card.
        print_data (dict): A dictionary of print run informaiton received by the metadata handler as printed on the card.
    """

    type = CardType.MONSTER
    id = None

    def __init__(self, **kwargs) -> None:
        # Perform insubstantiation to necessary fields from kwargs.
        self.type = kwargs["type"]  # CardType
        self.title = kwargs["title"]  # str
        stage_str = kwargs.get("stage")
        self.stage = StageType(stage_str) if stage_str else None
        # The mana_type is expected to be a ManaType enum object or None.
        # If it's None, we default to COLORLESS.
        self.mana_type = kwargs.get("mana_type") or ManaType.COLORLESS

        self.evolve_from = kwargs.get("evolve_from")  # str ?
        self.evolve_to = kwargs.get("evolve_to")  # str ?
        self.health = kwargs["health"]  # int
        self.weak_type = kwargs.get("weak_type")
        self.weak_mult = kwargs.get("weak_mult")
        self.resist_type = kwargs.get("resist_type")
        self.resist_val = kwargs.get("resist_val")  # int
        self.retreat_val = kwargs.get("retreat_val")  # int
        self.attacks = [Attack(**atk_data) for atk_data in kwargs["attacks"]]

        # Perform insubstantiation to optional fields from kwargs.
        self.abilities = kwargs.get("abilities", [])  # list: Ability
        self.level = kwargs.get("level")  # int
        self.dex_data = kwargs.get("dex_data", {})  # dict: JSON-esque
        self.print_data = kwargs.get("print_data", {})  # dict: JSON-esque


class MonsterCard(CardTemplate):
    """
    Active and mutable instance of a monster card, instantiated from a `MonsterTemplate`.\n
    A `MonsterCard` composes its classes through the data stored in a `MonsterTemplate` card.
    The`MonsterTemplate`s pull their card data, such as name, stage level, attacks, ability,
    and data, from dicts, and hold them for a `MonsterCard` to access. The way a `MonsterCard`
    accesses its parent's data is by pulling it from their `card` attribute (i.e., `card.id`.
    `card.mana_type`, `card_retreat_val`.)

    Attributes:
        card (MonsterTemplate): The card template that `MonsterCard`s refers to as a data source.
        health (int): The monster's live health, nominally expressed in multiples of 10.
        mana_pool (dict): Deprecated.
        attached_mana (dict): A container for attached mana cards, sorted by mana type.
        abilities (list): A list of abilities, drawn from the card template's ability data.
    """

    def __init__(self, card) -> None:
        """
        Initializes a `MonsterCard` unit. The superclass `CardTemplate` gives the `MonsterCard` a unique ID.

        Args:
            card (MonsterTemplate): The card template that `MonsterCard` refers to as a data source.
        """
        # Receive unique ID from superclass
        super().__init__()
        self.card = card
        self.health = self.card.health
        self.mana_pool = {mana_type: 0 for mana_type in ManaType}  # Deprecated
        self.attached_mana = {}
        self.special_conditions = {}
        self.prior_evos = []
        # Parse abilities into Effect instances
        self.abilities = [
            EffectRegistry.create_effect(ability_data)
            for ability_data in (self.card.abilities or [])
            if EffectRegistry.create_effect(ability_data) is not None
        ]
        logger.debug(f"Initiate {self.card.type} card ({self.id} {self.card.title})")

        #! STATE FLAGS
        self.has_attacked = False
        self.has_attached = False
        self.has_evolved = False

    @property
    def title(self):
        """Returns the title from the card template."""
        return self.card.title

    def use_attack(self, attack_index, player, target) -> bool:
        """Performs attack from the given index. Attacks take the form of dicts and are kept in a list.
        See the `Attack` class docstring for more info on attack execution.

        Args:
            attack_index (int): The numeric index of the attack.
            player (PlayerUnit): The player with the monster performing the attack.
            target (PlayerUnit): The player with the monster receiving the attack.
        """
        if 0 <= attack_index < len(self.card.attacks):
            attack = self.card.attacks[attack_index]
            attack.execute(player, target)
            return True
        else:
            print(
                f"Invalid attack index: {attack_index}. {self.card.title} does not have an attack at that position."
            )
            return False

    def take_damage(self, damage) -> None:
        """
        Reduces the monster's health by the given amount.

        Args:
            damage (int): The amount of damage to be taken.
        """
        self.health -= damage

    #! MANA METHODS
    @property
    def total_mana(self) -> dict[ManaType, int]:
        """
        A property that dynamically calculates the total available mana by combining
        the temporary mana_pool with mana from attached ManaCards.
        """
        # Start with a copy of the temporary mana pool
        combined_pool = self.mana_pool.copy()

        # Add mana from attached cards
        for mana_card in self.attached_mana.values():
            mana_type = mana_card.card.mana_type
            combined_pool[mana_type] = combined_pool.get(mana_type, 0) + 1

        return combined_pool

    def add_mana_attachment(self, mana_card) -> None:
        """Receives a ManaCard object and adds it to its attachments."""
        self.attached_mana[mana_card.id] = mana_card
        logger.info(f"Attached {mana_card.card.title} to {self.card.title}")

    def detach_mana_attachment(self, mana_card_id: int):
        """Removes and returns one specific ManaCard object from its attachments."""
        mana_card = self.attached_mana.pop(mana_card_id, None)
        return mana_card

    def discard_attached_mana(self, amount_to_discard: int) -> list:
        """
        Discards a specified number of attached mana cards.
        This is typically used for paying retreat costs.

        Args:
            amount_to_discard (int): The number of mana cards to discard.

        Returns:
            list: A list of the discarded ManaCard objects.
        """
        discarded_cards = []
        if amount_to_discard <= 0:
            return discarded_cards

        # Convert keys to a list to allow modification during iteration
        attached_ids = list(self.attached_mana.keys())
        for card_id in attached_ids[:amount_to_discard]:
            discarded_cards.append(self.attached_mana.pop(card_id))
        return discarded_cards

    def has_mana(self, cost):
        """
        Checks whether there is sufficent mana in the mana pool for performing
        an action that costs mana.

        :param cost: is the attack's cost—usually a dict like `{ManaType.FIRE: 2, ...}`
        """

        # Make a copy to not mutate original: what remains will be
        remaining_pool = self.total_mana.copy()

        # First, pay specific mana costs. Colorless costs are handled later
        for mana_type, amount in cost.items():
            if mana_type == ManaType.COLORLESS:
                continue
            if remaining_pool.get(mana_type, 0) < amount:
                return False
            remaining_pool[mana_type] -= amount

        # Handle colorless costs
        if ManaType.COLORLESS in cost:
            total_remaining = sum(remaining_pool.values())
            if total_remaining < cost[ManaType.COLORLESS]:
                return False

        return True

    def spend_mana(self, cost):
        """
        Spends mana during the exertion of a move that costs a specific quantity of mana.

        :param cost: Mana quantity, expressed in a dict like `{ManaType.FIRE: 2, ...}`, to be subtracted from the monster's mana pool.
        """
        # This method now only needs to spend from the temporary mana_pool.
        # The check in has_mana() already confirmed that attached cards can cover the rest.
        # We don't "spend" attached cards, they are just present.
        # This logic correctly prioritizes spending temporary mana first.

        # Pay non-colorless costs first
        for mana_type, amount in cost.items():
            if mana_type == ManaType.COLORLESS:
                continue
            self.mana_pool[mana_type] -= amount

        # Pay colorless costs
        if ManaType.COLORLESS in cost:
            colorless_needed = cost[ManaType.COLORLESS]
            for mana_type in ManaType:
                if colorless_needed <= 0:
                    break
                available = self.mana_pool[mana_type]
                to_spend = min(available, colorless_needed)
                self.mana_pool[mana_type] -= to_spend
                colorless_needed -= to_spend

    #! SPECIAL CONDITIONS
    def add_special_condition(self, type) -> None:
        """
        Adds a special condition.
        """
        self.special_conditions[type] = True

    def remove_special_condition(self, type) -> dict:
        """
        Removes and returns a special condition.
        """
        return self.special_conditions.pop(type, None)

    def handle_asleep(self) -> None:
        pass

    def handle_burned(self) -> None:
        pass

    def handle_confused(self) -> None:
        pass

    def handle_paralyzed(self) -> None:
        pass

    def handle_poisoned(self) -> None:
        pass
