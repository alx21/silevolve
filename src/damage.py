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
    
    
    def getAttacker(): return self.attacker
    def getAttackerName(): return self.attacker.getName()
    def getTarget(): return self.target
    def getDM(): return self.dm
    def getMoS(): return self.MoS
    def isKnockdown(): return self.knockdown
    def isAP(): return self.armor_piercing
    def isAimedAtHead(): return self.aimed_at_head
    def isKnockout(): return self.knockout
    def attackerGetsFreeStrike(): return self.attacker_gets_free_strike
    def defenderGetsFreeStrike(): return self.defender_gets_free_strike
    
    def applyDamage(self):
        return self.target.wound(self)
