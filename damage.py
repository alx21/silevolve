class Damage():
    def __init__(self,
            attacker = None,
            target = None,
            dm = 0,
            MoS = 0,
            knockdown = False,
            armor_piercing = False,
            aimed_at_head = False,
            knockout = False,
            attacker_gets_free_strike = False,
            defender_gets_free_strike = False):
        self.dm = dm
        self.MoS = MoS
        self.knockdown = knockdown and MoS > 0
        self.armor_piercing = armor_piercing
        self.aimed_at_head = aimed_at_head
        self.knockout = knockout and MoS > 0
        self.attacker_gets_free_strike = attacker_gets_free_strike
        self.defender_gets_free_strike = defender_gets_free_strike
        self.target = target
        self.attacker = attacker
        
    def getDamage(self): return max(self.MoS * self.dm, 0)
    
    def applyDamage(self):
        return self.target.wound(self)
