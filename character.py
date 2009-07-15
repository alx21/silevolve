import weaponlist
import silconstants as sil
import random

debug = False

class character():
    def __init__(self,
            name="Thug",
            dmg=8,
            attroll=(2,1),
            defroll=(2,1),
            stamina=25,
            armor=10,
            head_armored=False,
            init=(2,0),
            health=0,
            wounds=0,
            weapons=[weaponlist.meleeWeapon(), weaponlist.hth()],
            done=False):
        self.name=name
        self.attroll = attroll
        self.dmg = dmg
        self.defroll = defroll
        self.stamina = stamina
        self.armor = armor
        self.head_armored = head_armored
        self.init = init
        self.health = health
        self.wounds = wounds
        self.weapons = weapons
        self.done = done
        self.stance = (0,0,0) # (attack defense init attack_bonus) dice count mods
        self.prone = False
        self.has_used_free_strike = False
        self.multiple_attacker_penalty = 0
        self.attacker_list = []
        self.current_init = -1
        self.action_penalty = 0
        
    def setActionPenalty(self, penalty):
        self.action_penalty = penalty
        
    def clear(self):
        self.reset()
        self.stance = (0,0,0)
        self.wounds = 0
        self.done = False
        self.prone = False
        
    def getAIData(self):
        """ Returns the list of AI data relevant to this character """
        ai_data = [ self.dmg,
                    self.attroll[0],
                    self.attroll[1],
                    self.defroll[0],
                    self.defroll[1],
                    self.init[0],
                    self.init[1],
                    self.health,
                    self.stamina,
                    self.armor,
                    int(self.head_armored),
                    self.wounds,
                    self.action_penalty,
                    self.multiple_attacker_penalty,
                    int(self.has_used_free_strike),
                    self.stance[0],
                    self.stance[1],
                    self.stance[2],
                    self.current_init,
                    int(self.prone),
                    len(self.weapons) - 1 ]
                    
        for w in self.weapons:
            ai_data += w.getAIData()
            
        return ai_data
                    
        
    def wound(self, damage):
    
        self.incMultipleAttackerPenalty(damage.attacker)
    
        dmg = damage.getDamage()
        if dmg == 0: return False

        if (damage.aimed_at_head): dmg *= 2
        
        arm = self.armor
        if damage.aimed_at_head and not self.head_armored: arm = 0
        elif damage.armor_piercing: arm = arm // 2
    
        if dmg > self.stamina * 2 + arm:
            self.done = True
            if debug: print self.name, "has been instant deathed with damage:", dmg
        elif dmg > self.stamina + arm:
            self.wounds += -2
        elif dmg > self.stamina // 2 + arm:
            self.wounds += -1
        
        knockoutpenalty = 0
        if damage.knockout: knockoutpenalty = damage.MoS * -1
        print knockoutpenalty, "knockoutpenalty"
        
        if debug: print "DAMAGE: Target: ", self.name, " damage: ", dmg, " wounds: ", self.wounds, " map: ", self.multiple_attacker_penalty
        
        return self.done or self.healthCheck(knockoutpenalty)
        
    def healthCheck(self, knockoutpenalty = 0):
        if self.wounds*-1 >  5 + self.health:
            self.done = True
            if debug: print self.name, "has been removed from the fight by way of massive wound penalties!"
        else:
            roll = rollX(2, self.wounds + self.health + knockoutpenalty)
            if debug: print self.name, "health check: ", roll, "with health", self.health, "and penalty", knockoutpenalty
            if roll[1] or roll[0] < 1:
                self.done = True
                if debug: print self.name, "has been removed from the fight by way of KO!"
        return self.done
        
    def rollAtt(self, dicedropped=0):
        dice = self.attroll[0] + dicedropped + self.stance[0]
        bonus = self.attroll[1] + self.wounds + self.action_penalty
        roll = rollX(dice,bonus)
        if debug: print self.name, "attack rolling", dice, bonus, ":", roll
        return roll
        
    def rollDef(self, dicedropped=0):
        dice = self.defroll[0] + dicedropped + self.stance[1]
        prone = 0
        if self.prone: prone = -3
        bonus = self.defroll[1] + self.wounds + self.multiple_attacker_penalty + prone
        roll = rollX( dice, bonus  )
        if debug: print self.name, "defence rolling", dice, bonus, ":", roll
        return roll
        
    def setInit(self):
        i = self.rollInit()
        if i[1]: self.current_init = -1
        else: self.current_init = i[0]
        
    def rollInit(self):
        dice = self.init[0] + self.stance[2]
        bonus = self.init[1] + self.wounds
        roll = rollX( dice, bonus )
        if debug: print self.name, "init with", dice,bonus, ":", roll
        return roll

    def setStance(self,stance):
        self.stance = sil._STANCES[stance]
        
    def getMultipleAttackerPenalty(self):
        return self.multiple_attacker_penalty
        
    def incMultipleAttackerPenalty(self, attacker):
        if not attacker in self.attacker_list:
            self.multiple_attacker_penalty -= 1
            self.attacker_list.append(attacker)
        
    def getInit(self):
        return self.current_init
        
    def reset(self):
        """ Reset transitory combat-round stats for the new round """
        self.hasUsedFreeAttack = False
        self.multiple_attacker_penalty = 0
        self.attacker_list = []
        self.current_init = None
        self.action_penalty = 0

    def attack(self, enemies=None, target=None):
        # Rename this to action, perhaps
        # implement special actions maybe
        
        if not target:
            if not enemies: return None
            # a defined target means a free strike against a specific foe
            target = self.pickTarget(enemies)
            
        opts = dict({})
        weapon = self.pickWeapon()
        if debug: print "Picked weapon:", weapon
        attack_type = self.pickAttackType(weapon)
        if debug: print "Picked attack type:", attack_type
        opts[sil._ATT_TYPE] = attack_type
        
        opt_list = weapon.getAttackOptions()[attack_type]
        
        if sil._DICE_DROPPED in opt_list:
            # make sure that we can drop dice before asking the AI
            dice_dropped = self.pickDiceDropped()
            opts[sil._DICE_DROPPED] = dice_dropped
            
        if sil._ROF in opt_list:
            # if the weapon supports ROF, ask the AI
            rof = self.pickROF()
            opts[sil._ROF] = rof
        
        return weapon.attack(self, target, opts)
        
        
    
    #### AI SECTION ############################################################
    
    def pickWeapon(self):
        index = self.aiPickWeapon()
        if index > 0 and index < len(self.weapons):
            return self.weapons[index]
        return self.weapons[0] # kind default in this case
    
    def pickAttackType(self, weapon):
        # ALEX IF YOU ARE LOOKING FOR THIS ATTACK TYPE BUG
        # it is actually perfectly sane behaviour that you intentionally wrote
        # it is time to go to bed.
        index = self.aiPickAttackType()
        if index > 0 and index < len(weapon.types):
            return index
        return 0 # default attack
        
    def pickNumberOfActions(self):
        actions = self.aiPickNumberOfActions()
        if actions > 0:
            if actions > 3:
                return 3 # case where actions > 3
            return actions # case where actions is a reasonable number
        return 1 # case where actions is negative or zero. kind default.
    
    def pickStance(self):
        stance_index = self.aiPickStance()
        if stance_index in sil._STANCES.keys():
            self.setStance(stance_index)
        # implied "else: don't change stance"
                
    def pickTarget(self, enemies):
        enemy_index = self.aiPickTarget()
        if enemy_index >= 0 and enemy_index < len(enemies):
            return enemies[enemy_index]
        return enemies[0] # first enemy in list; kind default
        
    def pickDiceDropped(self):
        dice_dropped = self.aiPickDiceDropped()
        if dice_dropped < (self.attroll[0]*-1 - self.stance[0]):
            return (self.attroll[0]*-1 - self.stance[0])
        if dice_dropped > 0:
            return 0
        return dice_dropped
        
    def pickROF(self, weapon):
        rof = self.aiPickROF()
        if rof > weapon.rof:
            return weapon.rof
        if rof < 0:
            return 0
        return rof

    #### REPLACEABLE AI SLOTS ##################################################
    # The following classes can be replaced with AI functions.

    def aiPickStance(self):
        return 0

    def aiPickTarget(self):
        # won't be used for initial tests: mano a mano
        return 0

    def aiPickNumberOfActions(self):
        return 1
        
    def aiPickSpecialAction(self):
        # we using this yet?
        return 0
        
    def aiPickWeapon(self):
        return 0
        
    def aiPickDiceDropped(self):
        return 0
        
    def aiPickROF(self):
        # won't be used for initial tests; no ROF weapons expected
        return 0
        
    def aiPickAttackType(self):
        return 0
    
#### DICE ROLLER ###############################################################

def rollX(x,y=0):
    if (x < 1):
        ret = min( random.randint(1,6), random.randint(1,6) )
    else:
        ret = 0;
        for i in range( 0, x ):
            rand = random.randint(1,6)
            if rand == 6 and ret >= 6: ret += 1
            if rand > ret: ret = rand
    return (max(ret + y, 0), ret == 1)
