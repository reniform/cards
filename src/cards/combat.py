class Attack:
    """
    Defines any action taken by a live monster that induces damage. Holds the following values:
    ### Basic metadata
    * `name`: The name of the attack.
    * `damage`: The hit points to be removed as a result of the damage.
    * `cost`: The cost of the attack in mana, i.e. a dict of {ManaType: amount}.
    * `effects`: A list of effects of type `Effect`.
    """
    def __init__(self, name, damage, cost, effects):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.effects = effects
    
    def execute(self, attacker, target):
        if not attacker.active_monster.has_mana(self.cost):
            print(f"Not enough mana for {self.name}!")
            return
        
        attacker.active_monster.spend_mana(self.cost)
        target.active_monster.take_damage(self.damage)
        print(f"{self.name} dealt {self.damage} damage!")

class Effect:
    """"""