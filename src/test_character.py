import unittest
import character

class TestWounding(unittest.TestCase):

    class FakeDamage():
        def getDamage(self): return 0
        def getMoS(self): return 1
        def isAP(self): return False
        def isAP(self): return False
        def isKnockdown(self): return False
        def isAimedAtHead(self): return False
        def isKnockout(self): return False
        def getAttackerName(self): return "FakeName"

    def setUp(self):
        self.char = character.Character(stamina=30,armor=10)
        self.char.healthCheck = lambda m: False
        # PREVENTS accidental success due to knockout!
        self.damage = self.FakeDamage()
    
    def testInstantDeath(self):
        # This is the first and thus far only test I have written.
        # It uncovered a serious bug. Hot DAMN.
        for d in (70, 71, 100, 1000):
            self.damage.getDamage = lambda: d
            self.char.wound(self.damage)
            self.assert_( self.char.getDone() )
            self.setUp()
        
    def testDeepWound(self):
        for d in (40, 50, 69):
            self.damage.getDamage = lambda: d
            self.char.wound(self.damage)
            self.assertEqual( self.char.getWoundPenalty(), -2 )
            self.setUp()
        
    def testFleshWound(self):
        for d in (25, 30, 39):
            self.damage.getDamage = lambda: d
            self.char.wound(self.damage)
            self.assertEqual( self.char.getWoundPenalty(), -1 )
            self.setUp()
            
    def testNoWound(self):
        for d in (-10, 0, 10, 24):
            self.damage.getDamage = lambda: d
            self.char.wound(self.damage)
            self.assertEqual( self.char.getWoundPenalty(), 0 )
            self.setUp()


if __name__ == "__main__":
    unittest.main()
