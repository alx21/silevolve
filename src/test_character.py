import unittest
import character

class TestWounding(unittest.TestCase):

    class FakeDamage():
        def getDamage(self): return 0
        def getMoS(self): return 1
        def isAP(self): return False
        def isAP(self): return False
        def isKnockdown(self): return False
        def isKnockout(self): return False

    def setUp(self):
        self.char = character.Character(stamina=30,armour=10)
        self.damage = FakeDamage()
    
    def testInstantDeath(self):
        self.damage.getDamage = lambda: 70
        self.char.wound(instant_death_damage)
        self.assert_( self.char.done == True )


if __name__ == "__main__":
    unittest.main()
