from cards.enums import CardType

class MonsterTemplate:
    """
    **MonsterTemplate** holds base data.
    """
    type = CardType.MONSTER
    id   = 1
    def __init__(self, title, health, strength, attacks):
        self.title = title
        self.health = health
        self.strength = strength
        self.attacks = attacks

class MonsterCard(MonsterTemplate):
    """
    **MonsterCard** represents monster cards active in the player's deck.
    They are instantiated from the global data within a `MonsterTemplate`.
    """
    #def __init__(self, title, health, strength, attacks):
        #pass
        #super().__init__(title, health, strength, attacks)

    def __init__(self, card):
        self.card = card
        self.title = card.title
        self.health = card.health
        self.strength = card.strength
        self.attacks = card.attacks

    def use_attack(self, attack_index, player, target):
        """Performs attack from the given index"""
        attack = self.attacks[attack_index]
        attack.execute(player, target)
    
    def take_damage(self, damage):
        self.health -= damage