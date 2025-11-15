from cards.enums import CardType

class MonsterTemplate:
    """
    Immutable instance and static data source for monster cards. Holds the following values:
    ### Basic metadata
    * `title`: Monster name.
    * `health`: Hit points for the monster; maximum health is displayed with `max_health`.
    ### Play data
    * `attacks`: A list of attack-like actions to be taken by the monster in play. They are of type `Attack`, and may be chained with effects.
    """
    type = CardType.MONSTER
    id   = 1

    def __init__(self, title, health, attacks):
        self.title = title
        self.health = health
        self.max_health = health
        self.attacks = attacks

class MonsterCard(MonsterTemplate):
    """
    Active and mutable instance of a monster card, instantiated from a `MonsterTemplate`.
    """
    #def __init__(self, title, health, strength, attacks):
        #pass
        #super().__init__(title, health, strength, attacks)

    def __init__(self, card):
        self.card = card
        self.title = card.title
        self.health = card.health
        self.attacks = card.attacks

    def use_attack(self, attack_index, player, target):
        """Performs attack from the given index"""
        if 0 <= attack_index < len(self.attacks):
            attack = self.attacks[attack_index]
            attack.execute(player, target)
        else:
            print(f"Invalid attack index: {attack_index}. {self.title} does not have an attack at that position.")
            return False
    
    def take_damage(self, damage):
        self.health -= damage