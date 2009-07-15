import silconstants as sil
import damage

debug = False

class weapon():
    def __init__(self, name="", acc=0, dm=0, defense=0):
        self.name=name
        self.dm=dm
        self.acc=acc
        self.defense=defense
        self.br=0
        self.ammo=0
        self.rof=0
        self.pbb=0
        self.ap = False
        
    def getAIData():
        return [self.dm,
                self.acc,
                # self.br, canned for now to help prevent confusion
                self.defense,
                # self.ammo,
                # self.rof,
                # self.pbb,
                # int(self.ap)
                ]
                
                
    
    def getAttackOptions(self):
        """
        returns a tuple of the types of attacks possible, and the 
        options that are available corresponding with that attack.
        """
        typesList = []
        for k in self.types.keys():
            typesList.append(self.types[k][1])
        return (tuple(typesList))
    
    def attack(self, attacker, defender, opts):
        if not self.types.has_key(getFromDict(opts,sil._ATT_TYPE)):
            return self.types[sil._DEFAULT][0](attacker, defender, opts)
        else:
            return self.types[opts[sil._ATT_TYPE]][0](attacker, defender, opts)

            
class hth(weapon):
    def __init__(self,
                name="hth",
                acc=0,
                dm=0,
                defense=0 ):
        weapon.__init__(self, name, acc, dm, defense)
        self.types=dict({
            sil._HTH_KO: (self.hthAttackKnockout, (sil._DICE_DROPPED)),
            sil._HTH_KD: (self.hthAttackKnockdown, (sil._DICE_DROPPED)),
            sil._DEFAULT: (self.hthAttackStandard, (sil._DICE_DROPPED))
            })
        
    def hthAttackBase(self, attacker, defender, dicedropped=0, special=0):
        #if dicedropped == None: dicedropped = 0
        
        if debug: print "We're using the hand to hand attack base.", special
        
        attack = attacker.rollAtt(dicedropped + special)
        if debug: print attacker.name + " rolled " + repr(attack) + " on his attack."
        defense = defender.rollDef(dicedropped)
        if debug: print defender.name + " rolled " + repr(defense) + " on his defense."
        
        MoS = attack[0] - defense[0]
        if debug: print "The MoS is: " + repr(MoS)
        
        if attack[1]: return damage.Damage(target = defender, attacker=attacker)
        # this is a botch, so send back an empty damage
        
        return damage.Damage( dm = self.dm + attacker.dmg, MoS=MoS, attacker_gets_free_strike = defense[1], target = defender, attacker=attacker )
        
    def hthAttackStandard(self, attacker, defender, opts):
        return self.hthAttackBase(attacker, defender, getFromDict(opts, sil._DICE_DROPPED))
        
    def hthAttackKnockout(self, attacker, defender, opts):
        if debug: print "Attempting a knockout attack!"
        attack = self.hthAttackBase(attacker, defender, getFromDict(opts, sil._DICE_DROPPED), sil._CC_KNOCKOUT_PENALTY)
        attack.knockout = True
        return attack
        
    def hthAttackKnockdown(self, attacker, defender, opts):
        attack = self.hthAttackBase(attacker, defender, getFromDict(opts, sil._DICE_DROPPED), sil._CC_KNOCKDOWN_PENALTY)
        attack.knockdown = True
        return attack
        
class meleeWeapon(hth):
    def __init__(self, name="knife", 
                acc=0,
                dm=3,
                defense=0,
                ap = False ):
        hth.__init__(self, name, acc, dm, defense)
        self.ap=ap
        self.types=dict({sil._DEFAULT: (self.hthAttackStandard, (sil._DICE_DROPPED))})
    
class gun(weapon):
    def __init__(self, name="makarov", 
                acc=0,
                dm=15,
                br=5,
                ammo=12,
                rof=0,
                pbb=1, # point blank bonus
                defense=-2,
                ap = False ):
        weapon.__init__(self, name, acc, dm, defense)
        self.br=br
        self.ammo=ammo
        self.rof=rof
        self.pbb=pbb
        self.types=dict({
            sil._RA_ROF: (self.gunAttack, ( sil._ROF )),
            sil._RA_HS: (self.gunAttackHS, ()),
            sil._RA_B: (self.gunAttackBarrage, ()),
            sil._DEFAULT: (self.gunAttack, ())
        })
        self.ap=ap
    
    def gunAttack(self, attacker, defender, opts):
        # only for close combat for now!
        
        rof = getFromDict(opts, sil._ROF)
        
        attack = attacker.rollAtt()
        defense = defender.rollDef()
        
        MoS = attack[0] - defense[0] + self.pbb + self.acc
        
        # toss the ammo
        if rof==0: self.ammo -= 1
        else: self.ammo -= (rof * 5)
        
        # if attacker botches, forget the rest of the stuff
        if attack[1]: return damage.Damage(target=defender, attacker=attacker, defender_gets_free_strike=True)
        
        # if the MoS is negative or 0, return whether or not the defender
        # has botched in close combat
        if MoS < 1:
            return damage.Damage(attacker=attacker,target=defender,defender_gets_free_strike=True)
        
        #we will implement standard ROF rules here, no house rules yet
        return damage.Damage( dm = self.dm, MoS = MoS + rof, armor_piercing=self.ap, target=defender, attacker=attacker, defender_gets_free_strike=True)
        
    def gunAttackBarrage(self, attacker, defender):
        self.ammo -= 4
        return self.gunAttack(attacker, defender)
        
    def gunAttackHS(self, attacker, defender):
        damage = self.gunAttack(attacker, defender)
        damage.aimed_at_head = True
        return damage

    
def getFromDict(d,key):
    if d.has_key(key):
        return d[key]
    else:
        return 0


# Let's define some cool standard weapons!
ak47 = gun( name="AK47",
            acc=0,
            dm=28,
            br=50,
            ammo=30,
            rof=1,
            pbb=-1, # rather unwieldy up close
            defense=0,
            ap = False )
            
ak74 = gun( name="AK74",
            acc=0,
            dm=25,
            br=50,
            ammo=30,
            rof=1,
            pbb=-1, # rather unwieldy up close
            defense=0,
            ap = False )

iron_fist = meleeWeapon(name="Yuri's Iron Fist", acc=1, dm=3) # the acc is used to show
# the specialty of the fist's only likely wielder

staff = hth(name="Wooden Staff", dm=7, defense=1)
# I'm putting this in hth for now because I think some weapons should be capable
# of knockout and knockdown and it should be harder with others and I haven't
# clarified my thoughts on this yet.
