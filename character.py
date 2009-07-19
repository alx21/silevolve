import weaponlist
import silconstants as sil
import random

debug = False

class Character():
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
            weapons=[weaponlist.meleeWeapon(), weaponlist.hth()],
            done=False):
        self.name         = name
        self.attroll      = attroll
        self.dmg          = dmg
        self.defroll      = defroll
        self.stamina      = stamina
        self.armor        = armor
        self.head_armored = head_armored
        self.init         = init
        self.health       = health
        self.flesh_wounds = 0
        self.deep_wounds  = 0
        self.done         = done
        self.weapons      = weapons
        self.stance = (0,0,0) # (attack defense init attack_bonus) dice mods
        # note that 'focused' doesn't exist yet.
        self.prone                     = False
        self.has_used_free_strike      = False
        self.multiple_attacker_penalty = 0
        self.attacker_list             = []
        self.current_init              = -1
        self.action_penalty            = 0
        
    def setActionPenalty(self, penalty):
        self.action_penalty = penalty
        
    def clear(self):
        self.reset()
        self.stance = (0,0,0)
        self.deep_wounds  = 0
        self.flesh_wounds = 0
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
                    self.getWoundPenalty(),
                    self.action_penalty,
                    self.multiple_attacker_penalty,
                    int(self.has_used_free_strike),
                    self.stance[0],
                    self.stance[1],
                    self.stance[2],
                    self.current_init,
                    int(self.prone),
                    len(self.weapons) - 1 ]
                    
        # I'm not sure if this is the best way to represent weapon data ...
        for w in self.weapons:
            ai_data += w.getAIData()
            
        return ai_data
        
    def getWoundPenalty(self):
        return self.flesh_wounds + self.deep_wounds * 2
                    
        
    def wound(self, damage):
        """ Hurt a guy! Returns True if the victim has been offed or KOd """
    
        if debug: print " ** Applying damage to", self.name, "from", damage.attacker.name
    
        self.incMultipleAttackerPenalty(damage.attacker)
    
        dmg = damage.getDamage()
        if dmg == 0:
            if debug: print "  *", self.name, "but MAP incremented to:", self.getMultipleAttackerPenalty()
            return self.done # pretty much certainly false.

        if (damage.aimed_at_head): dmg *= 2
        
        arm = self.armor
        if damage.aimed_at_head and not self.head_armored: arm = 0
        elif damage.armor_piercing: arm = arm // 2
    
        if dmg > self.stamina * 2 + arm:
            self.done = True
            if debug:
                print "  *", self.name, "has been instant deathed with damage:", dmg
            return True
                
        elif dmg > self.stamina + arm:
            self.deep_wounds += -2
        elif dmg > self.stamina // 2 + arm:
            self.deep_wounds += -1
        
        knockoutpenalty = 0
        if damage.knockout: knockoutpenalty = damage.MoS * -1
        
        if damage.MoS > 0 and damage.knockdown:
            if debug: print "  *", self.name, "has fallen down and CAN'T GET UP"
            self.prone = True
        
        if debug:
            print "  * DAMAGE: Target: ", self.name, " damage: ", dmg, " wounds: ", self.getWoundPenalty(), " map: ", self.getMultipleAttackerPenalty()
        
        return self.healthCheck(knockoutpenalty)
        
    def healthCheck(self, knockoutpenalty = 0):
        if self.getWoundPenalty()*-1 >=  5 + self.health:
            self.done = True
            if debug:
                print "  *", self.name, "has been removed from the fight by way of  massive wound penalties!"
        else:
            roll = rollX(2, self.getWoundPenalty() + self.health + knockoutpenalty)
            
            if debug:
                print "  *", self.name, "health check: ", roll, "with health", self.health, " wounds", self.getWoundPenalty(), "and KO penalty", knockoutpenalty
            
            if roll[1] or roll[0] < 2:
                self.done = True
                
                if debug:
                    print " **", self.name, "has been removed from the fight by way of KO!"

        return self.done
        
    def rollAtt(self, dicedropped=0):
        dice = self.attroll[0] + dicedropped + self.stance[0]
        bonus = self.attroll[1] + self.getWoundPenalty() + self.action_penalty
        roll = rollX(dice,bonus)
        if debug: print "   ", self.name, "attack rolling", dice, bonus, ":", roll
        return roll
        
    def rollDef(self, dicedropped=0):
        dice = self.defroll[0] + dicedropped + self.stance[1]
        prone_penalty = 0
        if self.prone: prone_penalty = -3
        bonus = self.defroll[1] + self.getWoundPenalty() + self.getMultipleAttackerPenalty() + prone_penalty
        roll = rollX( dice, bonus  )
        if debug: print "   ", self.name, "defence rolling", dice, bonus, ":", roll
        return roll
        
    def setInit(self):
        i = self.rollInit()
        if i[1]: self.current_init = -1
        else: self.current_init = i[0]
        
    def rollInit(self):
        dice = self.init[0] + self.stance[2]
        bonus = self.init[1] + self.getWoundPenalty()
        roll = rollX( dice, bonus )
        if debug: print self.name, "init with", dice,bonus, ":", roll
        return roll

    def setStance(self,stance):
        self.stance = sil._STANCES[stance]
        
    def getMultipleAttackerPenalty(self):
        return min(3, self.multiple_attacker_penalty)
        
    def incMultipleAttackerPenalty(self, attacker):
        if not attacker in self.attacker_list:
            self.multiple_attacker_penalty -= 1
            self.attacker_list.append(attacker)
        
    def getInit(self):
        return self.current_init
        
    def reset(self):
        """ Reset transitory combat-round stats for the new round """
        self.has_used_free_strike = False
        self.multiple_attacker_penalty = 0
        self.attacker_list = []
        self.current_init = None
        self.action_penalty = 0

    def attack(self, enemies=None, target=None, data=[]):
        # Rename this to action, perhaps
        # implement special actions maybe
        
        if debug: print "***", self.name, "selects attack now!"
        
        if not target:
            if not enemies: return None
            # a defined target means a free strike against a specific foe
            target = self.pickTarget(enemies,data=data)
            
        opts = dict({})
        weapon = self.pickWeapon(data)
        if debug: print "    Picked:", weapon.name
        attack_type = self.pickAttackType(weapon,data)
        
        if debug: print "    Picked attack type:", attack_type
        
        opts[sil._ATT_TYPE] = attack_type
        
        opt_list = weapon.getAttackOptions()[attack_type]
        
        if sil._DICE_DROPPED in opt_list:
            # make sure that we can drop dice before asking the AI
            dice_dropped = self.pickDiceDropped(data)
            opts[sil._DICE_DROPPED] = dice_dropped
            
        if sil._ROF in opt_list:
            # if the weapon supports ROF, ask the AI
            rof = self.pickROF(data)
            opts[sil._ROF] = rof
        
        return weapon.attack(self, target, opts)
        
        
    
    #### AI SECTION ############################################################
    
    def pickWeapon(self,data=[]):
        index = self.aiPickWeapon(data)
        if index > 0 and index < len(self.weapons):
            return self.weapons[index]
        return self.weapons[0] # kind default in this case
    
    def pickAttackType(self, weapon,data=[]):
        # ALEX IF YOU ARE LOOKING FOR THIS ATTACK TYPE BUG
        # it is actually perfectly sane behaviour that you intentionally wrote
        # it is time to go to bed.
        index = self.aiPickAttackType(data)
        if index > 0 and index < len(weapon.types):
            return index
        return 0 # default attack
        
    def pickNumberOfActions(self,data=[]):
        actions = self.aiPickNumberOfActions(data)
        if actions > 0:
            if actions > 3:
                return 3 # case where actions > 3
            return actions # case where actions is a reasonable number
        return 1 # case where actions is negative or zero. kind default.
    
    def pickStance(self,data=[]):
        stance_index = self.aiPickStance(data)
        if stance_index in sil._STANCES.keys():
            self.setStance(stance_index)
        # implied "else: don't change stance"
                
    def pickTarget(self, enemies,data=[]):
        enemy_index = self.aiPickTarget(data)
        if enemy_index >= 0 and enemy_index < len(enemies):
            return enemies[enemy_index]
        return enemies[0] # first enemy in list; kind default
        
    def pickDiceDropped(self,data=[]):
        dice_dropped = self.aiPickDiceDropped(data)
        if dice_dropped < (self.attroll[0]*-1 - self.stance[0]):
            return (self.attroll[0]*-1 - self.stance[0])
        if dice_dropped > 0:
            return 0
        return dice_dropped
        
    def pickROF(self, weapon,data=[]):
        rof = self.aiPickROF(data)
        if rof > weapon.rof:
            return weapon.rof
        if rof < 0:
            return 0
        return rof
        
    def fillSlots(self,chromosome):
        slots = [ self.aiPickStance,
                  # self.aiPickTarget,
                  self.aiPickNumberOfActions,
                  # self.aiPickSpecialAction,
                  self.aiPickWeapon,
                  self.aiPickDiceDropped,
                  # self.aiPickROF,
                  self.aiPickAttackType ]

        i = 0
        
        for f in chromosome:
            slots[i] = f.interpret
            i+=1
            

    #### REPLACEABLE AI SLOTS ##################################################
    # The following classes can be replaced with AI functions.

    def aiPickStance(self,data=[]):
        return 0

    def aiPickTarget(self,data=[]):
        # won't be used for initial tests: mano a mano
        return 0

    def aiPickNumberOfActions(self,data=[]):
        return 1
        
    def aiPickSpecialAction(self,data=[]):
        # we using this yet?
        return 0
        
    def aiPickWeapon(self,data=[]):
        return 0
        
    def aiPickDiceDropped(self,data=[]):
        return 0
        
    def aiPickROF(self,data=[]):
        # won't be used for initial tests; no ROF weapons expected
        return 0
        
    def aiPickAttackType(self,data=[]):
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
