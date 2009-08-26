# hey bryce I've added some notes about python in here for you

# import a bunch of files from the src folder
from src import character
from src import combathandler
from src import weaponlist

# how to instantiate characters!

yuri = character.Character( name="Yuri",
                            dmg=11,
                            attroll=(4,2),
                            defroll=(4,2),
                            stamina=45,
                            armor=36,
                            head_armored=False,
                            init=(2,-1),
                            health=1,
                            weapons=[weaponlist.iron_fist,weaponlist.hth()] )

katsuro = character.Character(  name="Kaito Katsuro",
                                dmg=8,
                                attroll=(5,0),
                                defroll=(5,1),
                                stamina=35,
                                armor=0,
                                head_armored=False,
                                init=(2,0),
                                health=2,
                                weapons=[weaponlist.staff,weaponlist.hth()] )
                            
# a note about the weapons in those two characters; weaponlist.hth() inits
# a new instance of the hth class, whereas the iron_fist is an object defined
# in weaponlist. Be careful with that since they can be overwritten. And if more
# than one person is assigned an object, remember that it is an object and not
# a primitive ... shouldn't be a problem with the weapons, but just a heads-up

# heh it could be a problem with the weapons. It just occurred to me that giving
# the 'AK' to more than one person would mean that enemies could be sharing a
# clip. We might wanna fix that at some point. :P

thug1 = character.Character( name="Thug 1",
        weapons=[weaponlist.gun(), weaponlist.hth(), weaponlist.meleeWeapon()])
            
thug2 = character.Character(name="Thug 2", weapons=[weaponlist.meleeWeapon()])
# the default character is a good basic thug.
# melee weapon defaults to a knife.
thug3 = character.Character(name="Thug 3", weapons=[weaponlist.gun()])
thug4 = character.Character(name="Thug 4", weapons=[weaponlist.gun()])
thug5 = character.Character(name="Thug 5", weapons=[weaponlist.gun()])
thug6 = character.Character(name="Thug 6", weapons=[weaponlist.gun()])
thug7 = character.Character(name="Thug 7", weapons=[weaponlist.gun()])




#'lambda:' just means "return the following simple expression" and is a function

if __name__ == "__main__":
    # a little trick to make sure this stuff only runs if THIS is the file being
    # executed. The stuff above will execute if this file is 'import'ed

    # use anonymous functions to plug in simple data to test ai functions
    # Note to bryce: in python, function names are variables.
    # if you don't put () after them they are assignable, passable, etc
    thug1.aiPickStance = lambda x: 2 # aggressive
    thug1.aiPickDiceDropped = lambda x: 0 # no dice drop
    thug1.aiPickNumberOfActions = lambda x: 1 # one action
    thug1.aiPickAttackType = lambda x: 2 # attack type 1=knockout, 2=knockdown
    thug1.aiPickWeapon = lambda x: 1 # 2nd weapon is hth
    
    # comment the following lines if you don't want to hear LOTS of stuff
    # character.debug = True
    # combathandler.debug = True
    
    # the following is a situation similar to one I might use for early
    # evolution trials    
    
    team1 = [thug1]
    team2 = [thug2]

    
    for i in range(0,100):
        
        thug1.clear()
        thug2.clear()
    
        fight = combathandler.CombatHandler([team1, team2])
        
        while fight.combatRound():
            pass # don't do anything. The real business is the while condition.
            
        print i
        for t in (thug1, thug2):
            print t.name, "has been killed?", t.done, ", Has", t.getWoundPenalty(), "penalty"
        
    
