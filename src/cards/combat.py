class Attack:
    def __init__(self, name, damage, cost):
        # cost will be a dict of {ManaType: amount}
        self.name = name
        self.damage = damage
        self.cost = cost
    
    def execute(self, attacker, target):
        if not attacker.has_mana(self.cost):
            print(f"Not enough mana for {self.name}!")
            return
        
        attacker.spend_mana(self.cost)
        target.active_monster.take_damage(self.damage)
        print(f"{self.name} dealt {self.damage} damage!")